# 📊 Status — System & Project Status

Report the current state of the VPS and arifOS project.

## System Health
RUN free -h
RUN df -h /
RUN uptime
RUN docker ps 2>/dev/null || echo "Docker not running"

## Project Status
RUN cd /root/arifOS && git status --short
RUN cd /root/arifOS && git log --oneline -3
RUN cd /root/arifOS && .venv/bin/python -c "import core; print('core: OK')" 2>&1
RUN cd /root/arifOS && .venv/bin/python -c "import arifosmcp.transport; print('arifosmcp.transport: OK')" 2>&1

## Services
RUN systemctl is-active arifos-mcp 2>/dev/null || echo "arifos-mcp service not configured"
RUN systemctl is-active nginx 2>/dev/null || echo "nginx not running"

Summarize everything in a clean status table.
