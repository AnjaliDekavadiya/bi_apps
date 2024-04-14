/** @odoo-module */

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { patch } from "@web/core/utils/patch";

patch(PosStore.prototype, {
    // @Override
    async _processData(loadedData) {
        await super._processData(...arguments);
        var self = this
        var  MototrcycleType = loadedData['motorcycle.type'] || [];
        self.db.motorcycle_type = [];
        self.db.motorcycle_make = [];
        self.db.motorcycle_model = [];
        self.db.all_motorcycle = [];
        self.db.motorcycle_year = [];
        self.db.produt_search_string = {};
        self.db.motorcycle_model_by_id = {};
        self.db.motorcycle_make_by_id = {};
        self.db.motorcycle_year_by_id = {};
        if(MototrcycleType){
            
            for (const type of MototrcycleType) {
                self.db.motorcycle_type.push(type);
            }
        }

        var  Mototrcyclemake = loadedData['motorcycle.make'] || [];
        if(Mototrcyclemake){
            for (const make of Mototrcyclemake) {
                self.db.motorcycle_make.push(make)
                self.db.motorcycle_make_by_id[make.id] = make
            }
        }

        var  Mototrcyclemodel = loadedData['motorcycle.mmodel'] || [];
        if(Mototrcyclemodel){
            for (const model of Mototrcyclemodel) {
                self.db.motorcycle_model.push(model)
                self.db.motorcycle_model_by_id[model.id] = model
            }
        }

        var all_motorcycle = loadedData['motorcycle.motorcycle'] || [];
        if(all_motorcycle){
            for (const motorcycle of all_motorcycle) {
                self.db.all_motorcycle.push(motorcycle)
            }
        }

        var  MotorcycleYear = loadedData['motorcycle.year'] || [];
        if(MotorcycleYear){
            for (const motorcycle_year of MotorcycleYear) {
                self.db.motorcycle_year.push(motorcycle_year)
                self.db.motorcycle_year_by_id[motorcycle_year.id] = motorcycle_year
            }
        }
    }
});
