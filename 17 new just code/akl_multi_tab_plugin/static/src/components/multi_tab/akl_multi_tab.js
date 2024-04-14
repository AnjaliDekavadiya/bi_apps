/** @odoo-module **/

import { Component, useRef } from "@odoo/owl";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";


export class AklMultiTab extends Component {

    setup() {
        super.setup();
        this.tabContainerRef = useRef('tab_container');
    }

    _on_click_tab_close(action_info) {
        this.props.close_action(action_info);
    }

    _add_action_item(action_info) {
        this.action_infos.push(action_info)
    }

    _get_cur_active_tab() {
        if (this.current_action_info) {
            return this.current_action_info
        } else if (this.action_infos.length > 0) {
            return this.action_infos[this.action_infos.length - 1]
        } else {
            return null
        }
    }

    get action_infos() {
        return this.props.action_infos;
    }

    get current_action_info() {
        return this.action_infos.find(action_info => action_info.active);
    }

    get_menu_label(name) {
        switch (name) {
            case "Close Current Tab":
                return this.env._t('Close Current Tab');
            case "Close Other Tabs":
                return this.env._t('Close Other Tabs');
            case 'Close All Tabs':
                return this.env._t('Close All Tabs');
        }
    }

    _on_multi_tab_prev() {

        debugger
        if (this.action_infos.length == 0) {
            return;
        }

        var index = this.action_infos.indexOf(this.current_action_info)
        index = index - 1;
        if (index < 0) {
            if (this.action_infos.length > 1) {
                index = this.action_infos.length - 1;
            } else {
                return;
            }
        }

        // notify parent action change
        let action_info = this.action_infos[index];
        this.props.active_action(action_info);
        this.rollPage('auto', index);
    }

    _on_multi_tab_next() {

        if (this.action_infos.length <= 1) {
            return;
        }

        // find the action index
        var index = this.action_infos.indexOf(this.current_action_info)
        index = index + 1;
        if (index >= this.action_infos.length) {
            index = 0;
        }

        // change the current action info
        let action_info = this.action_infos[index];

        // notify parent action change
        this.props.active_action(action_info);
        this.rollPage('auto', index);
    }

    _on_click_tab_item(action_info) {

        // restore the action first
        var index = this.props.action_infos.indexOf(action_info)
        this.props.active_action(action_info);

        this.rollPage('auto', index);
    }

    _close_current_action() {
        if (this.current_action_info) {
            this.props.close_action(this.current_action_info);
        }
    }

    _close_other_action() {
        if (this.current_action_info) {
            this.props.close_other_action(this.current_action_info);
        }
    }

    _close_all_action() {
        this.props.close_all_action();
    }

    _get_display_name(action_info) {
        let ref_action = action_info.action.ref_action || action_info.action;
        while (ref_action && ref_action.ref_action && ref_action.ref_action !== ref_action) {
            ref_action = ref_action.ref_action;
        }
        return ref_action.display_name || ref_action.name || "New";
    }

    rollPage(type, index) {

        let tabsHeader = $(this.tabContainerRef.el.querySelector('.akl_page_items'));
        let li_items = tabsHeader.children('li')
        let outerWidth = tabsHeader.outerWidth()
        let tabsLeft = parseFloat(tabsHeader.css('left'));

        if (type === 'left') {
            if (!tabsLeft && tabsLeft <= 0) {
                return;
            }
            let prefLeft = -tabsLeft - outerWidth;
            li_items.each(function (index, item) {
                let li = $(item)
                let left = li.position().left;

                if (left >= prefLeft) {
                    tabsHeader.css('left', -left);
                    return false;
                }
            });
        } else if (type === 'auto') {
            let thisLi = li_items.eq(index)
            if (!thisLi[0]) {
                return
            };
            let thisLeft = thisLi.position().left;
            if (thisLeft < -tabsLeft) {
                return tabsHeader.css('left', -thisLeft);
            }
            if (thisLeft + thisLi.outerWidth() >= outerWidth - tabsLeft) {
                let subLeft = thisLeft + thisLi.outerWidth() - (outerWidth - tabsLeft);
                li_items.each(function (i, item) {
                    let li = $(item)
                    let left = li.position().left;
                    if (left + tabsLeft > 0) {
                        if (left - tabsLeft > subLeft) {
                            tabsHeader.css('left', -left);
                            return false;
                        }
                    }
                });
            }
        } else {
            li_items.each(function (i, item) {
                let li = $(item)
                let left = li.position().left;

                if (left + li.outerWidth() >= outerWidth - tabsLeft) {
                    tabsHeader.css('left', -left);
                    return false;
                }
            });
        }
    }
};

AklMultiTab.props = {
    action_infos: {
        type: Array,
    },
    close_action: {
        type: Function,
    },
    active_action: {
        type: Function,
    },
    close_cur_action: {
        type: Function,
    },
    close_other_action: {
        type: Function,
    },
    close_all_action: {
        type: Function,
    },
};

AklMultiTab.components = {
    Dropdown,
    DropdownItem,
};
AklMultiTab.template = "akl_multi_tab.tab";
