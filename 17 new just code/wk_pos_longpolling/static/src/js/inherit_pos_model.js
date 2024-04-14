/** @odoo-module */
/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* License URL : <https://store.webkul.com/license.html/> */


const UPDATE_BUS_PRESENCE_DELAY = 60000;

import { PosStore } from "@point_of_sale/app/store/pos_store";
import { session } from '@web/session';
import { PosDB } from "@point_of_sale/app/store/db";
import { unaccent } from "@web/core/utils/strings";
import { browser } from "@web/core/browser/browser";
import { patch } from "@web/core/utils/patch";
import { throttleForAnimation } from "@web/core/utils/timing";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
var globalSelf = {};
globalSelf.ProductScreen = ProductScreen

patch(PosStore.prototype, {
    async setup(env, { popup, orm, number_buffer, hardware_proxy, barcode_reader, ui }) {
      this.added_channel_list = [];
      this.bus_service = env.services["bus_service"];
      await super.setup(...arguments);
    },

    //@override
    async after_load_server_data() {
      var self = this
      return super.after_load_server_data(...arguments).then(function () {
        if (self.config.enable_pos_longpolling) {
          self.startpolling();
        }
      });
    },
    startpolling() {
      var self = this;
      const imStatusModelToIds = {};
      let updateBusPresenceTimeout;
      const LOCAL_STORAGE_PREFIX = "presence";
      let lastPresenceTime =
        browser.localStorage.getItem(
          `${LOCAL_STORAGE_PREFIX}.lastPresence`
        ) || new Date().getTime();
      const throttledUpdateBusPresence = throttleForAnimation(
        function updateBusPresence() {
          clearTimeout(updateBusPresenceTimeout);
          const now = new Date().getTime();
          self.bus_service.send("update_presence", {
            inactivity_period: now - lastPresenceTime,
            im_status_ids_by_model: { ...imStatusModelToIds },
          });
          updateBusPresenceTimeout = browser.setTimeout(
            throttledUpdateBusPresence,
            UPDATE_BUS_PRESENCE_DELAY
          );
        },
        UPDATE_BUS_PRESENCE_DELAY
      );
      var self = this;
      browser.setTimeout(throttledUpdateBusPresence, 250);
      self.bus_service.addEventListener("notification", self._onNotification);
      self.add_channel(self.get_formatted_channel_name());
      // self.bus_service.call("bus_service", "startPolling");
      self.bus_service.addEventListener(
        "reconnect",
        throttledUpdateBusPresence
      );
      globalSelf = self;
      console.log("############ started websocket #########");
    },

    get_formatted_channel_name(channel) {
      var self = this;
      return (
        session.db + "_wk_pos_longpolling" + "_" + String(self.config.id)
      );
    },

    add_channel(channel) {
      var self = this;
      // self.bus_service._isMasterTab = true;
      if (self.added_channel_list.indexOf(channel) === -1) {
        self.bus_service.addChannel(channel);
        self.added_channel_list.push(channel);
        console.log("############ added channel :: %s #########", channel);
      }
    },

    update_sync_status() {
      $(".pos_longpolling_status").addClass("active");
      $(".pos_longpolling_status .fa-refresh").removeClass("fa-spin");
      $(".pos_longpolling_status .fa-refresh").css({
        color: "rgb(94, 185, 55)",
      });
      console.log("############ websocket response received #########)");
    },

    _onNotification(notifications) {
      var self = this;
      $.each(notifications.detail, function (index, notification) {
        globalSelf.update_sync_status();
        if (notification.type === "websocket_status") {
          // changed the sync status of pos longpolling
          globalSelf.update_sync_status();
        }
        if (notification.type === "pos_data_update") {
          $.each(notification.payload, function (index, payload) {
            globalSelf._modify_pos_data(payload);
          });
          globalSelf.update_sync_status();
        }
      });
    },

    // update the pos data after getting the notification through longpolling
    _modify_pos_data(payload) {
      var self = this;
      if (payload.model_name === "res.partner") {
        if (payload.operation === "DELETE")
          self.delete_partner(payload.record_id);
        else {
          self.db.add_partners(payload.record);
          self.update_partner_screen();
          console.log(
            "############ Modified partners (ids :: %s ) through websocket ###########)",
            payload.record_id
          );
        }
      } else if (payload.model_name === "product.product") {
        if (payload.operation !== "DELETE")
          self.update_products(payload.record);
        else self.delete_products(payload.record_id);
      } else if (payload.model_name === "product.pricelist.item" && self.pricelists) {
        if (payload.operation === "DELETE")
          self.delete_pricelist([payload.record_id]);
        else if (payload.operation === "CREATE")
          self.load_new_pricelist(payload.record);
        else self.update_modified_pricelist(payload.record);
      } else if (payload.model_name === "account.tax") {
        if (payload.operation === "DELETE")
          self.delete_account_tax(payload.record);
        else if (payload.operation === "CREATE")
          self.load_new_account_tax(payload.record, payload.amount);
        else self.update_modified_tax(payload.record, payload.amount);
      }
    },

    delete_account_tax(taxes) {
      var self = this;
      $.each(taxes, function (index, tax) {
        if (self.taxes_by_id[tax.id]) {
          delete self.taxes_by_id[tax.id];
          self.taxes.splice(
            self.taxes.findIndex((a) => a.id === tax.id),
            1
          );
          console.log(
            "############ deleted taxes (ids :: %s ) through websocket ###########)",
            tax.id
          );
        }
      });
    },

    update_modified_tax(taxes, amount) {
      var self = this;
      $.each(taxes, function (index, tax) {
        if (self.taxes_by_id[tax.id]) {
          self.taxes_by_id[tax.id] = tax;
          self.taxes_by_id[tax.id].amount = amount;
          self.taxes_by_id[tax.id].children_tax_ids = _.map(
            tax.children_tax_ids,
            function (child_tax_id) {
              return self.taxes_by_id[child_tax_id];
            }
          );
          self.taxes[self.taxes.findIndex((a) => a.id === tax.id)] =
            self.taxes_by_id[tax.id];
          console.log(
            "############ updated taxes (ids :: %s ) through websocket ###########)",
            tax.id
          );
        }
      });
    },
    load_new_account_tax(taxes, amount) {
      var self = this;
      $.each(taxes, function (index, tax) {
        self.taxes_by_id[tax.id] = tax;
        self.taxes_by_id[tax.id].amount = amount;
        self.taxes_by_id[tax.id].children_tax_ids = _.map(
          tax.children_tax_ids,
          function (child_tax_id) {
            return self.taxes_by_id[child_tax_id];
          }
        );
        self.taxes.push(self.taxes_by_id[tax.id]);
        console.log(
          "############ loaded new taxes (ids :: %s ) through websocket ###########)",
          tax.id
        );
      });
    },

    load_new_pricelist(pricelist_items) {
      var self = this;
      var pricelist_by_id = {};
      $.each(self.pricelists, function (index, pricelist) {
        pricelist_by_id[pricelist.id] = pricelist;
      });
      if(Object.keys(pricelist_by_id).length){
        $.each(pricelist_items, function (index, item) {
          var pricelist = pricelist_by_id[item.pricelist_id[0]];
          pricelist.items.push(item);
          if (
            self.default_pricelist.items.findIndex((a) => a.id === item.id) != -1
          )
            self.default_pricelist.items[
              self.default_pricelist.items.findIndex((a) => a.id === item.id)
            ] = item;
          else self.default_pricelist.items.push(item);
          console.log(
            "############ loaded new pricelists (ids :: %s ) through websocket ###########)",
            item.id
          );
        });
      }
    },

    update_modified_pricelist(pricelist_items) {
      var self = this;
      var pricelist_by_id = {};
      $.each(self.pricelists, function (index, pricelist) {
        pricelist_by_id[pricelist.id] = pricelist;
      });
      if(Object.keys(pricelist_by_id).length){
        $.each(pricelist_items, function (index, item) {
          var pricelist = pricelist_by_id[item.pricelist_id[0]];
          if (pricelist.items.findIndex((a) => a.id === item.id) != -1)
            pricelist.items[
              pricelist.items.findIndex((a) => a.id === item.id)
            ] = item;
          else pricelist.items.push(item);
          if (
            self.default_pricelist.items.findIndex((a) => a.id === item.id) != -1
          )
            self.default_pricelist.items[
              self.default_pricelist.items.findIndex((a) => a.id === item.id)
            ] = item;
          else self.default_pricelist.items.push(item);
          console.log(
            "############ loaded new pricelists (ids :: %s ) through websocket ###########)",
            item.id
          );
          console.log(
            "############ updated pricelists (ids :: %s ) through websocket ###########)",
            item.id
          );
        });
    }
    },

    delete_pricelist(delete_pricelist_ids) {
      var self = this;
      if (delete_pricelist_ids.length) {
        $.each(self.pricelists, function (index, pricelist) {
          var new_items = [];
          $.each(pricelist.items, function (index, item) {
            if (delete_pricelist_ids.indexOf(item.id) === -1) {
              new_items.push(item);
            }
          });
          pricelist.items = new_items;
        });
        console.log(
          "############ deleted pricelists (ids :: %s ) through websocket ###########)",
          delete_pricelist_ids
        );
      }
    },

    update_products(products) {
      var self = this;
      $.each(products, function (index, product) {
        if (product.id in self.db.product_by_id) {
          delete self.db.product_by_id[product.id];
        }
      });
      self._loadProductProduct(products);
      self.update_product_screen();
    },

    delete_products(product_id) {
      var self = this;
      var temp = self.db.product_by_id;
      var product = temp[product_id];
      var categ_search_string = self.db._product_search_string(product);
      var new_categ_string_list = [];
      $.each(self.db.category_search_string, function (index, categ_string) {
        if (categ_string.indexOf(categ_search_string) != -1) {
          var regEx = new RegExp(categ_search_string, "g");
          var remove_string = categ_string.replace(regEx, "");
          new_categ_string_list.push(remove_string);
        } else new_categ_string_list.push(categ_string);
      });
      self.db.category_search_string = new_categ_string_list;
      delete temp[product_id];
      self.db.product_by_id = temp;
      var new_categ_list = [];
      var categories = self.db.product_by_category_id;
      $.each(categories, function (index, categ) {
        var deleted_element_index = categ.indexOf(product_id);
        categ.splice(deleted_element_index, 1);
        new_categ_list.push(categ);
      });
      self.db.product_by_category_id = new_categ_list;
      self.update_product_screen();
      console.log(
        "############ Deleted product (id :: %s ) through websocket ###########)",
        product_id
      );
    },

    update_partner_screen() {
      if ($(".load-customer-search").length)
        $(".load-customer-search").click();
    },

    update_product_screen() {
      if ($(".pos_longpolling_status").length) {
        $(".pos_longpolling_status").addClass("from_pos_model");
        $(".pos_longpolling_status").click();
      }
    },


    delete_partner(partner_id) {
      var self = this;
      var partner_sorted = self.db.partner_sorted;
      var data = self.db.get_partner_by_id(partner_id);
      if (data.barcode) {
        delete self.db.partner_by_barcode[data.barcode];
      }
      // remove one element at specified index
      partner_sorted.splice(_.indexOf(partner_sorted, partner_id), 1);
      delete self.db.partner_by_id[partner_id];
      console.log(
        "############ Deleted partner (id :: %s ) through websocket ###########)",
        partner_id
      );
      self.update_partner_screen();
    },
    destroy() {
      var self = this;
      $.each(self.added_channel_list, function (index, channel) {
        self.bus_service.call("bus_service", "deleteChannel", channel);
      });
      self.added_channel_list = [];
      return this._super();
    },
  });

patch(PosDB.prototype, {
  get_product_by_category: function (category_id) {
    var product_ids = this.product_by_category_id[category_id];
    var list = [];
    if (product_ids) {
      for (
        var i = 0, len = Math.min(product_ids.length, this.limit);
        i < len;
        i++
      ) {
        const product = this.product_by_id[product_ids[i]];
        if (!(product.active && product.available_in_pos)) continue;
        if (!list.filter((a) => a.id === product.id).length)
          list.push(product);
      }
    }
    return list;
  },
  search_product_in_category: function (category_id, query) {
    try {
      query = query.replace(
        /[\[\]\(\)\+\*\?\.\-\!\&\^\$\|\~\_\{\}\:\,\\\/]/g,
        "."
      );
      query = query.replace(/ /g, ".+");
      var re = RegExp("([0-9]+):.*?" + unaccent(query), "gi");
    } catch (_e) {
      return [];
    }
    var results = [];
    for (var i = 0; i < this.limit; i++) {
      var r = re.exec(this.category_search_string[category_id]);
      if (r) {
        var id = Number(r[1]);
        const product = this.get_product_by_id(id);
        if (!(product.active && product.available_in_pos)) continue;
        if (!results.filter((a) => a.id === product.id).length)
          results.push(product);
      } else {
        break;
      }
    }
    return results;
  },
});
