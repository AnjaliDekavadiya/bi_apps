/** @odoo-module **/

import { SearchBar } from "@web/search/search_bar/search_bar";
import { SearchMenu } from "@oi_web_search/search_menu/search_menu";

SearchBar.components = {
    ...SearchBar.components,
    SearchMenu
};
