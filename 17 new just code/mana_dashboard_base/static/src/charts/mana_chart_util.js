/** @odoo-module alias=mana_dashboard.chart_util default=false **/

export let render_block = (name, icon) => {
    return () => {
        return `<div class="d-flex flex-column align-items-center justify-content-center"><div class="chart-icon">${icon}</div><div class='anita-block-label'>${name}</div></div>`
    }
}

export let default_chart_trait = []
