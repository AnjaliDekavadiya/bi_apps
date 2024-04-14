/** @odoo-module alias=mana_dashboard.search_button **/

import { BlockRegistry } from '@mana_dashboard_base/mana_block_registry';
import { icons } from "@mana_dashboard_base/utils/mana_icons";
import { BlockBase } from "@mana_dashboard_base/mana_block_base";

const BaseModel = BlockBase.BaseModel;
const BaseView = BlockBase.BaseView;

import { _t } from "@web/core/l10n/translation";

let sizes = {
    'lg': 'Large',
    'sm': 'Small'
};    

let btn_styles = [
    'primary',
    'secondary',
    'success',
    'info',
    'warning',
    'danger',
    'light',
    'dark',
];

const capitalize = (phrase) => {
    return phrase
        .toLowerCase()
        .split(' ')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
  };

function builder(editor, options) {

    const dc = editor.DomComponents;

    editor.BlockManager.add('search_button', {
        label: _t('Search Button'),
        category: _t('Search'),
        select: true,
        render: () => {
            return `<div class="d-flex flex-column align-items-center justify-content-center"><div class="chart-icon">${icons.search_button}</div><div class='anita-block-label'>Button</div></div>`
        },
        content: '<button class="btn btn-primary search_button">Apply</button>'
    });

    dc.addType('search_button', {
        model: BaseModel.extend({

            defaults: {
                ...BaseModel.prototype.defaults,
                tagName: 'Button',
                draggable: '.search_group',
                name: _t('Search Button'),
                classes: ['search_button', 'ml-1'],
                traits: [
                    {
                        type: 'select',
                        name: 'type',
                        label: 'type',
                        options: [
                            { value: 'Apply', name: 'Apply' },
                            { value: 'Reset', name: 'Reset' },
                        ]
                    },
                    {
                        type: 'text',
                        name: 'text',
                        label: 'Text',
                        changeProp: 1
                    },
                    {
                        type: 'class_select',
                        options: [
                            {value: '', name: 'Default'},
                            ... Object.keys(sizes).map((k) => { return {value: `btn-${k}`, name: sizes[k]} })
                        ],
                        label: 'Size'
                    },
                    {
                        type: 'class_select',
                        options: [
                            {value: '', name: 'None'},
                            ... btn_styles.map((v) => { return {value: `btn-${v}`, name: capitalize(v)} }),
                            ... btn_styles.map((v) => { return {value: `btn-outline-${v}`, name: capitalize(v) + ' (Outline)'} })
                        ],
                        label: 'Style'
                    },
                ],
                attributes: {
                    'type': 'Apply',
                    'text': 'Apply',
                }
            },

            initialize() {
                BaseModel.prototype.initialize.apply(this, arguments);
            },

            init() {
                const comps = this.components();
                const tChild = comps.length === 1 && comps.models[0];
                const chCnt = (tChild && tChild.is('textnode') && tChild.get('content')) || '';
                const text = chCnt || this.get('text');
                this.set('text', text);
                this.on('change:text', this.__onTextChange);
                (text !== chCnt) && this.__onTextChange();
            },

            __onTextChange() {
                this.components(this.get('text'));
            }

        }, {
            isComponent: (el) => {
                if (el && el.classList && el.classList.contains('search_button')) {
                    return { type: 'search_button' };
                }
            }
        }),

        view: BaseView.extend({

            init() {
                BaseView.prototype.init.apply(this, arguments);
            },

            removed() {
                BaseView.prototype.removed.apply(this, arguments);
            },

            __onTextChange() {
                this.components(this.get('text'));
            },

            render(...args) {
                BaseView.prototype.render.apply(this, args);
                return this;
            }
        })
    });
}

BlockRegistry.add('search_button', builder);
