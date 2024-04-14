/** @odoo-module alias=mana_dashboard.resize_manager **/

const resizeHandler = function (entries) {
    for (let entry of entries) {
        const listeners = entry.target.__resizeListeners__ || [];
        if (listeners.length) {
            console.log(listeners.length);
            listeners.forEach((fn) => {
                requestAnimationFrame(() => {
                    fn.call(entry.target, entry);
                });
            });
        }
    }
};

const addResizeListener = function (element, fn) {
    if (!element.__resizeListeners__) {
        element.__resizeListeners__ = [];
        element.__ro__ = new ResizeObserver(resizeHandler);
        element.__ro__.observe(element, {
            box: 'border-box',
            default: false,
        });
    }
    element.__resizeListeners__.push(fn);
};

const removeResizeListener = function (element, fn) {

    if (!element || !element.__resizeListeners__) return;
    if (fn) {
        element.__resizeListeners__.splice(
            element.__resizeListeners__.indexOf(fn), 1);
    } else {
        element.__resizeListeners__ = [];
    }
    if (!element.__resizeListeners__.length) {
        element.__ro__.disconnect();
        element.__resizeListeners__ = undefined;
    }
};

export const ResizeManager = {
    addResizeListener,
    removeResizeListener,
}
