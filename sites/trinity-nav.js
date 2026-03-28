/**
 * arifOS Trinity Navigation & Sync Engine
 * Ensures all trinity sites (HUMAN, THEORY, APPS) are linked and synchronized.
 */

(function() {
    const TRINITY_CONFIG = {
        HUMAN: {
            name: "HUMAN",
            url: "https://arif-fazil.com/",
            description: "Sovereign Profile · Scars · Authority",
            color: "#ff4d4f"
        },
        THEORY: {
            name: "THEORY",
            url: "https://arifos.arif-fazil.com/",
            description: "Constitutional Doctrine · 13 Floors",
            color: "#ffd24a"
        },
        APPS: {
            name: "APPS",
            url: "https://arifosmcp.arif-fazil.com/",
            description: "Developer Portal · MCP Runtime",
            color: "#2563eb"
        }
    };

    function injectTrinityStrip() {
        const currentHost = window.location.hostname;
        let activeNode = "";
        
        if (currentHost.includes("arifosmcp")) activeNode = "APPS";
        else if (currentHost.includes("arifos.")) activeNode = "THEORY";
        else if (currentHost.includes("arif-fazil.com") && !currentHost.includes("arifos")) activeNode = "HUMAN";

        // Create strip if it doesn't exist
        if (!document.querySelector('.trinity-strip-global')) {
            const strip = document.createElement('div');
            strip.className = 'trinity-strip-global';
            
            // Dynamic Styles
            const style = document.createElement('style');
            style.textContent = `
                .trinity-strip-global {
                    display: flex;
                    width: 100%;
                    height: 4px;
                    position: fixed;
                    top: 0;
                    left: 0;
                    z-index: 9999;
                    background: #000;
                }
                .trinity-node-segment {
                    flex: 1;
                    height: 100%;
                    transition: height 0.2s ease;
                    cursor: pointer;
                    position: relative;
                }
                .trinity-node-segment:hover {
                    height: 8px;
                }
                .trinity-node-segment.human { background: ${TRINITY_CONFIG.HUMAN.color}; }
                .trinity-node-segment.theory { background: ${TRINITY_CONFIG.THEORY.color}; }
                .trinity-node-segment.apps { background: ${TRINITY_CONFIG.APPS.color}; }
                
                /* Tooltip-like label on hover */
                .trinity-node-segment::after {
                    content: attr(data-label);
                    position: absolute;
                    top: 10px;
                    left: 50%;
                    transform: translateX(-50%) translateY(-10px);
                    background: rgba(0,0,0,0.9);
                    color: #fff;
                    padding: 4px 10px;
                    border-radius: 4px;
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 0.6rem;
                    white-space: nowrap;
                    opacity: 0;
                    pointer-events: none;
                    transition: all 0.2s ease;
                    border: 1px solid rgba(255,255,255,0.1);
                }
                .trinity-node-segment:hover::after {
                    opacity: 1;
                    transform: translateX(-50%) translateY(0);
                }
            `;
            document.head.appendChild(style);

            // Segments
            Object.keys(TRINITY_CONFIG).forEach(key => {
                const seg = document.createElement('div');
                seg.className = `trinity-node-segment ${key.toLowerCase()}`;
                seg.setAttribute('data-label', `${key}: ${TRINITY_CONFIG[key].description}`);
                seg.onclick = () => window.location.href = TRINITY_CONFIG[key].url;
                strip.appendChild(seg);
            });

            document.body.appendChild(strip);
        }
        
        // Sync any existing trinity-nodes/links on the page
        document.querySelectorAll('.trinity-node, .trinity-strip a, .nav-link').forEach(node => {
            const text = node.textContent.trim().toUpperCase();
            if (TRINITY_CONFIG[text]) {
                node.href = TRINITY_CONFIG[text].url;
                if (text === activeNode) {
                    node.classList.add('active');
                    node.style.borderBottom = `2px solid ${TRINITY_CONFIG[text].color}`;
                }
            }
        });

        // Special handling for the "ARIF OS" logo links
        document.querySelectorAll('a[href*="arif-fazil.com"]').forEach(link => {
            if (link.textContent.includes("ARIF") || link.querySelector('span')?.textContent.includes("ARIF")) {
                link.href = TRINITY_CONFIG.HUMAN.url;
            }
        });

        // Inject WebMCP Bridge
        if (!document.querySelector('script[src*="webmcp-bridge"]')) {
            const bridge = document.createElement('script');
            bridge.src = "https://arifosmcp.arif-fazil.com/static-sites/webmcp-bridge.js";
            document.head.appendChild(bridge);
        }
    }

    // Auto-init
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', injectTrinityStrip);
    } else {
        injectTrinityStrip();
    }
    
    // Periodically re-sync in case of dynamic SPA renders
    setInterval(injectTrinityStrip, 3000);
})();
