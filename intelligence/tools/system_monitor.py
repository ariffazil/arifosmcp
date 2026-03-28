"""
arifosmcp.intelligence/tools/system_monitor.py — System Health Sensor

ACLIP Console tool: gives AI agents clean JSON system metrics.
Replaces ad-hoc PowerShell scripts with structured, queryable output.
"""

from __future__ import annotations

import datetime
import json
import os
import platform
import subprocess
import time
from typing import Any

from arifosmcp.intelligence.tools.aclip_base import PSUTIL_OK, ok, partial, psutil, void


def _is_running_in_container() -> bool:
    """Detect if running inside a Docker/LXC container."""
    # Check for .dockerenv file
    if os.path.exists("/.dockerenv"):
        return True
    # Check cgroup
    try:
        with open("/proc/1/cgroup", "r") as f:
            return "docker" in f.read() or "lxc" in f.read()
    except Exception:
        pass
    return False


def get_resource_usage(
    include_swap: bool = True,
    include_io: bool = False,
    include_temp: bool = False,
) -> dict[str, Any]:
    """Return current RAM, CPU, disk, and sensor usage as structured JSON."""
    container_mode = _is_running_in_container()

    if PSUTIL_OK:
        try:
            data: dict[str, Any] = {}

            # 1. CPU
            cpu_percent = psutil.cpu_percent(interval=0.01)
            try:
                cpu_load = psutil.getloadavg()
            except (AttributeError, OSError):
                # getloadavg() not available on Windows or in some containers
                cpu_load = (0.0, 0.0, 0.0)

            data["cpu"] = {
                "percent": cpu_percent,
                "cores": psutil.cpu_count(logical=False),
                "logical": psutil.cpu_count(logical=True),
                "load_avg_1m": cpu_load[0],
                "load_avg_5m": cpu_load[1],
                "load_avg_15m": cpu_load[2],
                "load_1m": cpu_load[0],
                "load_5m": cpu_load[1],
                "load_15m": cpu_load[2],
            }

            # 2. Memory
            mem = psutil.virtual_memory()
            data["memory"] = {
                "total": mem.total,
                "available": mem.available,
                "used": mem.used,
                "free": mem.free,
                "usage_percent": mem.percent,
                "total_gb": round(mem.total / 1e9, 1),
                "used_gb": round(mem.used / 1e9, 1),
                "percent": mem.percent,  # Duplicate for compatibility
            }
            if include_swap:
                try:
                    swap = psutil.swap_memory()
                    data["memory"]["swap"] = {
                        "total": swap.total,
                        "used": swap.used,
                        "free": swap.free,
                        "percent": swap.percent,
                    }
                except Exception:
                    data["memory"]["swap"] = {"warning": "swap_info_unavailable"}

            # 3. Disk
            try:
                root_path = os.path.abspath(os.sep)
                disk = psutil.disk_usage(root_path)
                data["disk"] = {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "usage_percent": disk.percent,
                    "total_gb": round(disk.total / 1e9, 1),
                    "used_gb": round(disk.used / 1e9, 1),
                    "percent": disk.percent,  # Duplicate for compatibility
                }
            except Exception as e:
                data["disk"] = {"warning": f"disk_info_unavailable: {e}"}

            # 4. IO
            if include_io:
                try:
                    net_io = psutil.net_io_counters()
                    disk_io = psutil.disk_io_counters()
                    data["io"] = {
                        "network": {
                            "bytes_sent_gb": round(net_io.bytes_sent / 1e9, 2),
                            "bytes_recv_gb": round(net_io.bytes_recv / 1e9, 2),
                        },
                        "disk": {
                            "read_gb": round(disk_io.read_bytes / 1e9, 2),
                            "write_gb": round(disk_io.write_bytes / 1e9, 2),
                        },
                    }
                except Exception as e:
                    data["io"] = {"warning": f"io_counters_unavailable: {e}"}

            # 5. Thermal
            if include_temp:
                if hasattr(psutil, "sensors_temperatures"):
                    try:
                        temps = psutil.sensors_temperatures()
                        data["thermal"] = {
                            k: [v.current for v in vals] for k, vals in temps.items()
                        }
                    except Exception:
                        data["thermal"] = {"warning": "thermal_sensors_not_available"}
                else:
                    data["thermal"] = {"warning": "thermal_sensors_not_available"}

            data["platform"] = platform.system()
            try:
                data["uptime_seconds"] = round(time.time() - psutil.boot_time(), 1)
            except Exception:
                data["uptime_seconds"] = 0

            if container_mode:
                data["container_mode"] = True
                data["note"] = "Running in container - some metrics may be limited"

            return ok(data)

        except Exception as e:
            return void(f"psutil runtime error: {e}", "Check system permissions")
    else:
        return _fallback_wmi_usage()


def list_processes(
    filter_name: str | None = None,
    filter_user: str | None = None,
    min_cpu_percent: float = 0.0,
    min_memory_mb: float = 0.0,
    limit: int = 15,
    include_threads: bool = False,
) -> dict[str, Any]:
    """List and filter system processes with resource insights."""
    if not PSUTIL_OK:
        return void("psutil not installed", "uv pip install psutil")

    procs = []
    access_denied_count = 0

    for p in psutil.process_iter(
        ["pid", "name", "memory_info", "cpu_percent", "username", "create_time", "num_threads"]
    ):
        try:
            info = p.info
            name = info["name"] or ""
            user = info["username"] or "unknown"

            # Filters
            if filter_name and filter_name.lower() not in name.lower():
                continue
            if filter_user and filter_user.lower() not in user.lower():
                continue

            mem_mb = round((info["memory_info"].rss if info["memory_info"] else 0) / 1e6, 1)
            cpu_pct = round(info["cpu_percent"] or 0.0, 1)

            if mem_mb < min_memory_mb:
                continue
            if cpu_pct < min_cpu_percent:
                continue

            proc_data = {
                "pid": info["pid"],
                "name": name,
                "ram_mb": mem_mb,
                "cpu_pct": cpu_pct,
                "cpu_percent": cpu_pct,
                "user": user,
                "created": datetime.datetime.fromtimestamp(info["create_time"]).isoformat(),
            }
            if include_threads:
                proc_data["threads"] = info["num_threads"]

            procs.append(proc_data)

        except psutil.NoSuchProcess:
            continue
        except psutil.AccessDenied:
            access_denied_count += 1
            continue
        except MemoryError:
            continue

    # Sort by RAM by default
    procs.sort(key=lambda x: x["ram_mb"], reverse=True)

    result = {
        "total_count": len(procs[:limit]),
        "processes": procs[:limit],
    }

    if access_denied_count > 0:
        result["note"] = (
            f"Access denied to {access_denied_count} processes (container restrictions)"
        )

    if not procs and access_denied_count > 0:
        return partial(
            result, warning="All processes access denied - likely running in restricted container"
        )

    return ok(result)


def get_system_health(
    include_swap: bool = True,
    include_io: bool = False,
    include_temp: bool = False,
) -> dict[str, Any]:
    """Combined health report: resources + top RAM consumers + warnings."""
    usage = get_resource_usage(
        include_swap=include_swap, include_io=include_io, include_temp=include_temp
    )
    if usage.get("status") == "VOID":
        return usage

    res = usage
    procs = list_processes(limit=10)

    warnings = []

    def _pct(node, key):
        # res is already flattened by ok()
        return res.get(node, {}).get(key, 0)

    if _pct("memory", "percent") > 85:
        warnings.append(f"HIGH RAM: {_pct('memory', 'percent')}% used")
    if _pct("disk", "percent") > 88:
        warnings.append(f"HIGH DISK: {_pct('disk', 'percent')}% used (C:\\)")
    if _pct("cpu", "percent") > 80:
        warnings.append(f"HIGH CPU: {_pct('cpu', 'percent')}%")

    # Load average check
    logical_cores = res.get("cpu", {}).get("logical", 1)
    load_1m = res.get("cpu", {}).get("load_avg_1m", 0)
    if logical_cores and load_1m > logical_cores * 0.9:
        warnings.append(f"HIGH CPU LOAD (1m): {load_1m}")

    # Merge resources into result for a flatter structure
    result_data = {**res}
    result_data["top_processes"] = procs.get("processes", [])

    if not warnings:
        return ok(result_data)
    else:
        return partial(result_data, warning="; ".join(warnings), warnings=warnings)


def _fallback_wmi_usage() -> dict[str, Any]:
    """PowerShell-based fallback for Windows when psutil is unavailable."""
    script = (
        "$mem = Get-WmiObject Win32_OperatingSystem; "
        "$disk = Get-WmiObject Win32_LogicalDisk -Filter \"DeviceID='C:'\"; "
        "$cpu = (Get-WmiObject Win32_Processor).LoadPercentage; "
        "Write-Output (ConvertTo-Json @{"
        "  ram_total=[math]::Round($mem.TotalVisibleMemorySize/1MB,1);"
        "  ram_free=[math]::Round($mem.FreePhysicalMemory/1MB,1);"
        "  disk_free=[math]::Round($disk.FreeSpace/1GB,1);"
        "  disk_total=[math]::Round($disk.Size/1GB,1);"
        "  cpu=$cpu"
        "})"
    )
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", script],
            capture_output=True,
            text=True,
            timeout=10,
        )

        data = json.loads(result.stdout.strip())
        ram_total = data.get("ram_total", 0)
        ram_free = data.get("ram_free", 0)
        disk_total = data.get("disk_total", 0)
        disk_free = data.get("disk_free", 0)

        usage = {
            "source": "wmi_fallback",
            "ram": {
                "total_gb": ram_total,
                "free_gb": ram_free,
                "used_gb": round(ram_total - ram_free, 1),
                "percent": round((ram_total - ram_free) / ram_total * 100, 1) if ram_total else 0,
            },
            "cpu": {"percent": data.get("cpu", 0)},
            "disk_c": {
                "total_gb": disk_total,
                "free_gb": disk_free,
                "used_gb": round(disk_total - disk_free, 1),
                "percent": (
                    round((disk_total - disk_free) / disk_total * 100, 1) if disk_total else 0
                ),
            },
            "platform": "Windows",
        }
        return ok(usage)
    except Exception as e:
        return void(f"WMI fallback failed: {e}", "Install psutil for better reliability")
