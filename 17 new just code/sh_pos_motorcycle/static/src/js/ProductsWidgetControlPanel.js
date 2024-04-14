/** @odoo-module */

import { ProductsWidget } from "@point_of_sale/app/screens/product_screen/product_list/product_list";
import { patch } from "@web/core/utils/patch";
import { Component } from "@odoo/owl";
import { useState } from "@odoo/owl";
import { onMounted } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { unaccent } from "@web/core/utils/strings";

patch(ProductsWidget.prototype, {
    setup() {
        super.setup()
        this.pos = usePos();
        this.state = useState({ searchWord: '' });
        this.motorcycle_results;
        onMounted(() => {
            if (this.pos.config.sh_hide_search_bar_for_mobile) {
                if ($('.sh_search_box')) {
                    for (const each_serach_bar of $('.sh_search_box')) {
                        $(each_serach_bar).addClass('sh_hide_search')
                    }
                }
            }
            var motorcycle_types = $(document).find('#motorcycle_types')
            var motorcycle_makes = $(document).find('#motorcycle_makes')
            var motorcycle_models = $(document).find('#motorcycle_models')
            var motorcycle_years = $(document).find('#motorcycle_years')
            $(document).find('#motorcycle_make').attr({ disabled: true })
            $(document).find('#motorcycle_model').attr({ disabled: true })
            $(document).find('#motorcycle_year').attr({ disabled: true })
            if (motorcycle_types.val()) {
                $(document).find('#motorcycle_make').attr({ disabled: false })
            }
            for (const motorcycle_type of this.pos.db.motorcycle_type) {
                var option = document.createElement('option')
                motorcycle_types.append($(option).val(motorcycle_type.display_name))
            }
            for (const motorcycle_make of this.pos.db.motorcycle_make) {
                var option = document.createElement('option')
                motorcycle_makes.append($(option).val(motorcycle_make.display_name))
            }

            for (const motorcycle_model of this.pos.db.motorcycle_model) {
                var option = document.createElement('option')
                motorcycle_models.append($(option).val(motorcycle_model.display_name))
            }

            for (const motorcycle_year of this.pos.db.motorcycle_year) {
                var option = document.createElement('option')
                motorcycle_years.append($(option).val(motorcycle_year.display_name))
            }
        })
    },
    _clearMotorCycleSearch() {
        this.autopart_ids = []
        this.render()
    },
    _motorcycles(product_ids) {
        this.autopart_ids = product_ids
        this.productsToDisplay
        this.render()
    },
    get productsToDisplay() {
        var res = []
        var self = this
        var list = []
        if (this.pos.config.enable_search) {
            if (this.searchWord !== '') {
                if ($('#motorcycle_year').val()) {
                    return self.pos.db.search_product_in_motorcycle(self.selectedCategoryId, self.searchWord)
                } else {
                    return this.pos.db.search_product_in_category(
                        this.selectedCategoryId,
                        this.searchWord
                    );
                }
            } else if (this.autopart_ids) {
                var rec = this.pos.db.get_product_by_motorcycle(this.autopart_ids)
                var search_string;
                var data =''
                for (const i of rec) {
                    if (i) {
                        search_string = unaccent(self.pos.db._product_search_string(i));
                        if(self.pos.db.produt_search_string[self.selectedCategoryId] === undefined){
                            self.pos.db.produt_search_string[self.selectedCategoryId] = '';
                        }
                        data = data+search_string
                        res.push(i)
                    }
                }
                self.pos.db.produt_search_string[self.selectedCategoryId] = data
                if ($('#motorcycle_year').val()) {
                    return res
                } else {
                    return this.pos.db.get_product_by_category(this.selectedCategoryId)
                }
            }
            else {
                list = this.pos.db.get_product_by_category(this.selectedCategoryId);
                return list.sort(function (a, b) { return a.display_name.localeCompare(b.display_name) });
            }
        } else {
            return super.productsToDisplay
        }
    },
    clearType_search(event) {
        $(document).find('#motorcycle_type').val('')
        $(document).find('#motorcycle_make').val('')
        $(document).find('#motorcycle_model').val('')
        $(document).find('#motorcycle_make').attr({ disabled: true })
        $(document).find('#motorcycle_model').attr({ disabled: true })
        $(document).find('#motorcycle_year').val('')
        $(document).find('#motorcycle_year').attr({ disabled: true })
        this._clearMotorCycleSearch()
    },
    clear_make_search(event) {
        $(document).find('#motorcycle_make').val('')
        $(document).find('#motorcycle_model').val('')
        $(document).find('#motorcycle_model').attr({ disabled: true })
        $(document).find('#motorcycle_year').val('')
        $(document).find('#motorcycle_year').attr({ disabled: true })
        this._clearMotorCycleSearch()
    },
    clearModelSearch(event) {
        $(document).find('#motorcycle_model').val('')
        $(document).find('#motorcycle_year').val('')
        $(document).find('#motorcycle_year').attr({ disabled: true })
        this._clearMotorCycleSearch()
    },
    clearYearSearch(event) {
        $(document).find('#motorcycle_year').val('')
        this._clearMotorCycleSearch()
    },
    SearchMotorcycleType(event) {
        var motorcycle_make = $(document).find('#motorcycle_makes')
        if (event.target.value != '') {
            $(document).find('#motorcycle_make').attr({ disabled: false })
        } else {
            this.clearType_search()
            this.clear_make_search()
        }
        this.state.searchWord = event.target.value
        var res = this.pos.db.get_make_by_type(event.target.value)

        for (const each of res) {
            var option = document.createElement('option')
            var val = $(option).val(each.make_id[1])
            var a = motorcycle_make.find('option')
            for (var i = 0; i < a.length; i++) {
                if ($(a[i]).val() == each.make_id[1]) {
                    $(a[i]).remove()
                }
            }
            motorcycle_make.append(val)
        }
    },
    SearchMotorcycleMake(event) {
        var motorcycle_model = $(document).find('#motorcycle_models')
        if (event.target.value != '') {
            $(document).find('#motorcycle_model').attr({ disabled: false })
        } else {
            this.clearModelSearch()
        }
        var type = $(document).find('#motorcycle_type').val()
        var res = this.pos.db.get_model_by_make_and_type(event.target.value, type)

        for (const each of res) {
            var option = document.createElement('option')
            var val = $(option).val(each.display_name)
            var a = motorcycle_model.find('option')
            for (var i = 0; i < a.length; i++) {
                if ($(a[i]).val() == each.display_name) {
                    $(a[i]).remove()
                }
            }
            motorcycle_model.append(val)
        }
    },
    SearchMotorcycleModel(event) {
        var motorcycle_year = $(document).find('#motorcycle_years')
        if (event.target.value != '') {
            $(document).find('#motorcycle_year').attr({ disabled: false })
        } else {
            this.clearModelSearch()
        }
        var res = this.pos.db.get_motorcycle_by_model(event.target.value)
        this.motorcycle_results = res
        if (res.length > 0) {
            $(document).find('#motorcycle_year').attr({ disabled: false })

            for (const each of res) {
                if (each.year_id[1] == each.end_year_id[1]) {
                    var option = document.createElement('option')
                    var val = $(option).val(each.year_id[1])
                    motorcycle_year.append(val)
                } else {
                    for (var i = parseInt(each.year_id[1]); i <= parseInt(each.end_year_id[1]); i++) {
                        var option = document.createElement('option')
                        var val = $(option).val(i)
                        motorcycle_year.append(val)
                    }
                }
            }
        }

    },
    SearchMotorcycleyear(event) {
        var product_lst = []
        var Products = this.pos.db.product_by_id
        if (this.pos.config.enable_common_search && this.pos.config.enable_search) {
            const filter_product = Object.values(this.pos.db.product_by_id).filter((p) =>  p.available_in_pos && p.sh_is_common_product);
            for (const product of filter_product) {
                if (product.sh_is_common_product) {
                    product_lst.push(product.id)
                }
            }
        }
        if (this.motorcycle_results) {
            for (const each of this.motorcycle_results) {
                if (each) {
                    for (var i = 0; i < each.product_ids.length; i++) {
                        if (!product_lst.includes(each.product_ids[i])) {
                            product_lst.push(each.product_ids[i])
                        }
                    }
                }
            }
        }
        this._motorcycles(product_lst)
    }
    
});

