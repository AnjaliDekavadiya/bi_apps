/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";
import { useService } from "@web/core/utils/hooks";


patch(PosStore.prototype, {
    
    async _processData(loadedData) {
        await super._processData(loadedData);
        this.session_list_data();
        this.users_list_data();
    },
    async session_list_data(){
        const session_data = await this.orm.call(
            'pos.session', 
            'search_read',
            
        );
        this.sessions_list = session_data
    },
    async users_list_data(){
        const user_data = await this.orm.call(
            'res.users',
            'search_read',
            
        );
        this.users = user_data
    },
    
});