/* ═══════════════════════════════════════════════════════════════════════
   Relicta Dashboard — interactividad
   - Llamadas a las APIs (servicio propio, aliado, adapter, tareas async)
   - Animación de contadores
   - Reveal on scroll + toasts
   ═══════════════════════════════════════════════════════════════════════ */

(function () {
    "use strict";

    // ── CSRF token para peticiones POST ──
    function getCookie(name) {
        const m = document.cookie.match("(^|;)\\s*" + name + "\\s*=\\s*([^;]+)");
        return m ? m.pop() : "";
    }
    const CSRF = getCookie("csrftoken");

    // ── Toast ──
    const toast = document.getElementById("toast");
    let toastTimer;
    function showToast(msg, type = "ok") {
        toast.textContent = msg;
        toast.className = "toast show " + type;
        clearTimeout(toastTimer);
        toastTimer = setTimeout(() => (toast.className = "toast"), 3200);
    }

    // ── Render de JSON en un <pre> ──
    function renderOutput(id, data) {
        const el = document.getElementById(id);
        if (!el) return;
        el.textContent = JSON.stringify(data, null, 2);
        el.classList.add("show");
    }

    // ── Helpers de fetch ──
    async function apiGet(url) {
        const r = await fetch(url, { headers: { Accept: "application/json" } });
        return { ok: r.ok, data: await r.json() };
    }
    async function apiPost(url, body) {
        const r = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": CSRF,
                Accept: "application/json",
            },
            body: JSON.stringify(body || {}),
        });
        return { ok: r.ok, data: await r.json() };
    }

    function withLoading(btn, fn) {
        return async function () {
            btn.classList.add("loading");
            try {
                await fn();
            } catch (e) {
                showToast("Error: " + e.message, "err");
            } finally {
                btn.classList.remove("loading");
            }
        };
    }

    // ── Acciones por botón (data-action) ──
    const actions = {
        async info(btn) {
            const { ok, data } = await apiGet("/api/v1/info/");
            renderOutput("out-info", data);
            showToast(ok ? "✓ Info del sistema obtenida" : "✗ Error", ok ? "ok" : "err");
        },

        async aliado(btn) {
            const { ok, data } = await apiGet("/api/v1/aliado/");
            renderOutput("out-aliado", data);
            const disp = data && data.disponible;
            showToast(disp ? "✓ Aliado respondió" : "⚠ Aliado no disponible", disp ? "ok" : "err");
        },

        async conversion(btn) {
            const monto = document.getElementById("conv-monto").value || 0;
            const origen = document.getElementById("conv-origen").value;
            const destino = document.getElementById("conv-destino").value;
            const { ok, data } = await apiGet(
                `/api/v1/conversion/?monto=${monto}&origen=${origen}&destino=${destino}`
            );
            renderOutput("out-conversion", data);
            const res = document.getElementById("conv-result");
            if (ok && data.monto_convertido !== undefined) {
                res.textContent = `${data.monto_origen} ${data.moneda_origen} = ${data.monto_convertido} ${data.moneda_destino}`;
                showToast(`✓ Convertido vía ${data.proveedor}`, "ok");
            } else {
                res.textContent = "—";
                showToast("✗ " + (data.error || "Error"), "err");
            }
        },

        async reporte(btn) {
            const { ok, data } = await apiPost("/api/v1/tareas/reporte/");
            renderOutput("out-tareas", data);
            showToast(ok ? "⚙ Reporte encolado (async)" : "✗ Error", ok ? "ok" : "err");
        },

        async notificacion(btn) {
            const { ok, data } = await apiPost("/api/v1/tareas/notificacion/", {
                reserva_id: 1,
                email: "demo@relicta.com",
            });
            renderOutput("out-tareas", data);
            showToast(ok ? "⚙ Notificación encolada (async)" : "✗ Error", ok ? "ok" : "err");
        },
    };

    document.querySelectorAll("[data-action]").forEach((btn) => {
        const name = btn.getAttribute("data-action");
        if (actions[name]) {
            btn.addEventListener("click", withLoading(btn, () => actions[name](btn)));
        }
    });

    // ── Animación de contadores ──
    function animateCount(el) {
        const target = parseInt(el.dataset.count, 10) || 0;
        const dur = 900;
        const start = performance.now();
        function tick(now) {
            const p = Math.min((now - start) / dur, 1);
            const eased = 1 - Math.pow(1 - p, 3);
            el.textContent = Math.round(target * eased);
            if (p < 1) requestAnimationFrame(tick);
        }
        requestAnimationFrame(tick);
    }

    // ── Reveal on scroll ──
    const io = new IntersectionObserver(
        (entries) => {
            entries.forEach((e) => {
                if (e.isIntersecting) {
                    e.target.classList.add("in");
                    e.target.querySelectorAll?.("[data-count]").forEach(animateCount);
                    if (e.target.hasAttribute?.("data-count")) animateCount(e.target);
                    io.unobserve(e.target);
                }
            });
        },
        { threshold: 0.15 }
    );
    document.querySelectorAll(".reveal").forEach((el) => io.observe(el));
    // Contadores dentro de métricas (por si ya están visibles)
    document.querySelectorAll(".metric-value[data-count]").forEach((el) => io.observe(el.closest(".reveal") || el));
})();
