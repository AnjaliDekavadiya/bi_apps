/** @odoo-module alias=mana_dashboard.date_util **/

import { BlockRegistry } from '@mana_dashboard_base/mana_block_registry';

function get_this_year() {
    let date = moment();
    let start = moment(date).startOf('year');
    let end = moment(date).endOf('year');
    return [start.format('YYYY-MM-DD HH:mm:ss'), end.format('YYYY-MM-DD HH:mm:ss')];
}

function get_this_month() {
    let date = moment();
    let start = moment(date).startOf('month');
    let end = moment(date).endOf('month');
    return [start.format('YYYY-MM-DD HH:mm:ss'), end.format('YYYY-MM-DD HH:mm:ss')];
}

function get_this_week() {
    let date = moment();
    let start = moment(date).startOf('week');
    let end = moment(date).endOf('week');
    return [start.format('YYYY-MM-DD HH:mm:ss'), end.format('YYYY-MM-DD HH:mm:ss')];
}

function get_today() {
    let date = moment();
    let start = moment(date).startOf('day');
    let end = moment(date).endOf('day');
    return [start.format('YYYY-MM-DD HH:mm:ss'), end.format('YYYY-MM-DD HH:mm:ss')];
}

function get_next_year() {
    let date = moment();
    let start = moment(date).add(1, 'year').startOf('year');
    let end = moment(date).add(1, 'year').endOf('year');
    return [start.format('YYYY-MM-DD HH:mm:ss'), end.format('YYYY-MM-DD HH:mm:ss')];
}

function get_next_month() {
    let date = moment();
    let start = moment(date).add(1, 'month').startOf('month');
    let end = moment(date).add(1, 'month').endOf('month');
    return [start.format('YYYY-MM-DD HH:mm:ss'), end.format('YYYY-MM-DD HH:mm:ss')];
}

function get_next_week() {
    let date = moment();
    let start = moment(date).add(1, 'week').startOf('week');
    let end = moment(date).add(1, 'week').endOf('week');
    return [start.format('YYYY-MM-DD HH:mm:ss'), end.format('YYYY-MM-DD HH:mm:ss')];
}

function get_tomorrow() {
    let date = moment();
    let start = moment(date).add(1, 'day').startOf('day');
    let end = moment(date).add(1, 'day').endOf('day');
    return [start.format('YYYY-MM-DD HH:mm:ss'), end.format('YYYY-MM-DD HH:mm:ss')];
}

function get_last_year() {
    let date = moment();
    let start = moment(date).subtract(1, 'year').startOf('year');
    let end = moment(date).subtract(1, 'year').endOf('year');
    return [start.format('YYYY-MM-DD HH:mm:ss'), end.format('YYYY-MM-DD HH:mm:ss')];
}

function get_last_month() {
    let date = moment();
    let start = moment(date).subtract(1, 'month').startOf('month');
    let end = moment(date).subtract(1, 'month').endOf('month');
    return [start.format('YYYY-MM-DD HH:mm:ss'), end.format('YYYY-MM-DD HH:mm:ss')];
}

function get_last_week() {
    let date = moment();
    let start = moment(date).subtract(1, 'week').startOf('week');
    let end = moment(date).subtract(1, 'week').endOf('week');
    return [start.format('YYYY-MM-DD'), end.format('YYYY-MM-DD')];
}

function get_yesterday() {
    let date = moment();
    let start = moment(date).subtract(1, 'day').startOf('day');
    let end = moment(date).subtract(1, 'day').endOf('day');
    return [start.format('YYYY-MM-DD HH:mm:ss'), end.format('YYYY-MM-DD HH:mm:ss')];
}

function get_last_7_days() {
    let date = moment();
    let start = moment(date).subtract(7, 'day').startOf('day');
    let end = moment(date).endOf('day');
    return [start.format('YYYY-MM-DD HH:mm:ss'), end.format('YYYY-MM-DD HH:mm:ss')];
}

function get_last_30_days() {
    let date = moment();
    let start = moment(date).subtract(30, 'day').startOf('day');
    let end = moment(date).endOf('day');
    return [start.format('YYYY-MM-DD HH:mm:ss'), end.format('YYYY-MM-DD HH:mm:ss')];
}

function get_last_90_days() {
    let date = moment();
    let start = moment(date).subtract(90, 'day').startOf('day');
    let end = moment(date).endOf('day');
    return [start.format('YYYY-MM-DD HH:mm:ss'), end.format('YYYY-MM-DD HH:mm:ss')];
}

function get_last_365_days() {
    let date = moment();
    let start = moment(date).subtract(365, 'day').startOf('day');
    let end = moment(date).endOf('day');
    return [start.format('YYYY-MM-DD HH:mm:ss'), end.format('YYYY-MM-DD HH:mm:ss')];
}

function get_next_7_days() {
    let date = moment();
    let start = moment(date).startOf('day');
    let end = moment(date).add(7, 'day').endOf('day');
    return [start.format('YYYY-MM-DD HH:mm:ss'), end.format('YYYY-MM-DD HH:mm:ss')];
}

function get_next_30_days() {
    let date = moment();
    let start = moment(date).startOf('day');
    let end = moment(date).add(30, 'day').endOf('day');
    return [start.format('YYYY-MM-DD HH:mm:ss'), end.format('YYYY-MM-DD HH:mm:ss')];
}

function get_next_90_days() {
    let date = moment();
    let start = moment(date).startOf('day');
    let end = moment(date).add(90, 'day').endOf('day');
    return [start.format('YYYY-MM-DD HH:mm:ss'), end.format('YYYY-MM-DD HH:mm:ss')];
}

function get_next_365_days() {
    let date = moment();
    let start = moment(date).startOf('day');
    let end = moment(date).add(365, 'day').endOf('day');
    return [start.format('YYYY-MM-DD HH:mm:ss'), end.format('YYYY-MM-DD HH:mm:ss')];
}

function get_this_month() {
    let date = moment();
    let start = moment(date).startOf('month');
    let end = moment(date).endOf('month');
    return [start.format('YYYY-MM-DD HH:mm:ss'), end.format('YYYY-MM-DD HH:mm:ss')];
}

function get_this_week() {
    let date = moment();
    let start = moment(date).startOf('week');
    let end = moment(date).endOf('week');
    return [start.format('YYYY-MM-DD HH:mm:ss'), end.format('YYYY-MM-DD HH:mm:ss')];
}

function get_today() {
    let date = moment();
    let start = moment(date).startOf('day');
    let end = moment(date).endOf('day');
    return [start.format('YYYY-MM-DD HH:mm:ss'), end.format('YYYY-MM-DD HH:mm:ss')];
}

function get_this_quarter() {
    let date = moment();
    let start = moment(date).startOf('quarter');
    let end = moment(date).endOf('quarter');
    return [start.format('YYYY-MM-DD HH:mm:ss'), end.format('YYYY-MM-DD HH:mm:ss')];
}

function get_last_quarter() {
    let date = moment();
    let start = moment(date).subtract(1, 'quarter').startOf('quarter');
    let end = moment(date).subtract(1, 'quarter').endOf('quarter');
    return [start.format('YYYY-MM-DD HH:mm:ss'), end.format('YYYY-MM-DD HH:mm:ss')];
}

function get_next_quarter() {
    let date = moment();
    let start = moment(date).add(1, 'quarter').startOf('quarter');
    let end = moment(date).add(1, 'quarter').endOf('quarter');
    return [start.format('YYYY-MM-DD HH:mm:ss'), end.format('YYYY-MM-DD HH:mm:ss')];
}

function get_next_year() {
    let date = moment();
    let start = moment(date).add(1, 'year').startOf('year');
    let end = moment(date).add(1, 'year').endOf('year');
    return [start.format('YYYY-MM-DD HH:mm:ss'), end.format('YYYY-MM-DD HH:mm:ss')];
}

function get_last_month() {
    let date = moment();
    let start = moment(date).subtract(1, 'month').startOf('month');
    let end = moment(date).subtract(1, 'month').endOf('month');
    return [start.format('YYYY-MM-DD HH:mm:ss'), end.format('YYYY-MM-DD HH:mm:ss')];
}

function get_last_week() {
    let date = moment();
    let start = moment(date).subtract(1, 'week').startOf('week');
    let end = moment(date).subtract(1, 'week').endOf('week');
    return [start.format('YYYY-MM-DD HH:mm:ss'), end.format('YYYY-MM-DD HH:mm:ss')];
}

function get_last_7_days() {
    let date = moment();
    let start = moment(date).subtract(7, 'day').startOf('day');
    let end = moment(date).endOf('day');
    return [start.format('YYYY-MM-DD HH:mm:ss'), end.format('YYYY-MM-DD HH:mm:ss')];
}

function get_last_30_days() {
    let date = moment();
    let start = moment(date).subtract(30, 'day').startOf('day');
    let end = moment(date).endOf('day');
    return [start.format('YYYY-MM-DD HH:mm:ss'), end.format('YYYY-MM-DD HH:mm:ss')];
}

function get_last_90_days() {
    let date = moment();
    let start = moment(date).subtract(90, 'day').startOf('day');
    let end = moment(date).endOf('day');
    return [start.format('YYYY-MM-DD HH:mm:ss'), end.format('YYYY-MM-DD HH:mm:ss')];
}

function get_last_365_days() {
    let date = moment();
    let start = moment(date).subtract(365, 'day').startOf('day');
    let end = moment(date).endOf('day');
    return [start.format('YYYY-MM-DD HH:mm:ss'), end.format('YYYY-MM-DD HH:mm:ss')];
}

let date_ranges = {
    'All Time': [moment('2010-01-01'), moment('2050-12-31')],
    'This Year': [moment().startOf('year'), moment().endOf('year')],
    'This Month': [moment().startOf('month'), moment().endOf('month')],
    'This Week': [moment().startOf('week'), moment().endOf('week')],
    'Today': [moment().startOf('day'), moment().endOf('day')],
    'This Quarter': [moment().startOf('quarter'), moment().endOf('quarter')],
    'Last Quarter': [moment().subtract(1, 'quarter').startOf('quarter'), moment().subtract(1, 'quarter').endOf('quarter')],
    'Next Quarter': [moment().add(1, 'quarter').startOf('quarter'), moment().add(1, 'quarter').endOf('quarter')],
    'Next Year': [moment().add(1, 'year').startOf('year'), moment().add(1, 'year').endOf('year')],
    'Last Month': [moment().subtract(1, 'month').startOf('month'), moment().subtract(1, 'month').endOf('month')],
    'Last Week': [moment().subtract(1, 'week').startOf('week'), moment().subtract(1, 'week').endOf('week')],
    'Last 7 Days': [moment().subtract(7, 'day').startOf('day'), moment().endOf('day')],
    'Last 30 Days': [moment().subtract(30, 'day').startOf('day'), moment().endOf('day')],
    'Last 90 Days': [moment().subtract(90, 'day').startOf('day'), moment().endOf('day')],
    'Last 365 Days': [moment().subtract(365, 'day').startOf('day'), moment().endOf('day')],
    'Next Month': [moment().add(1, 'month').startOf('month'), moment().add(1, 'month').endOf('month')],
    'Next Week': [moment().add(1, 'week').startOf('week'), moment().add(1, 'week').endOf('week')],
    'Yesterday': [moment().subtract(1, 'day').startOf('day'), moment().subtract(1, 'day').endOf('day')],
    'Tomorrow': [moment().add(1, 'day').startOf('day'), moment().add(1, 'day').endOf('day')],
};

// return all the function by order
export const date_utils = {
    get_this_year: get_this_year,
    get_this_month: get_this_month,
    get_this_week: get_this_week,
    get_today: get_today,
    get_yesterday: get_yesterday,
    get_tomorrow: get_tomorrow,
    get_this_quarter: get_this_quarter,
    get_last_quarter: get_last_quarter,
    get_next_quarter: get_next_quarter,
    get_next_year: get_next_year,
    get_next_month: get_next_month,
    get_next_week: get_next_week,
    get_last_year: get_last_year,
    get_last_month: get_last_month,
    get_last_week: get_last_week,
    get_last_7_days: get_last_7_days,
    get_last_30_days: get_last_30_days,
    get_last_90_days: get_last_90_days,
    get_last_365_days: get_last_365_days,
    
    // next 7 days
    get_next_7_days: get_next_7_days,
    get_next_30_days: get_next_30_days,
    get_next_90_days: get_next_90_days,
    get_next_365_days: get_next_365_days,
    
    date_ranges: date_ranges,
}
