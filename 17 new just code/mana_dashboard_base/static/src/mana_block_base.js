/** @odoo-module alias=mana_dashboard.block_base **/

import { assets } from "@web/core/assets";
import { renderToString } from "@web/core/utils/render";

const Component = grapesjs.Component;
const ComponentView = grapesjs.ComponentView;

const defaultModel = Component;
const defaultView = ComponentView;

import { icons } from "@mana_dashboard_base/utils/mana_icons";
import { Config } from "@mana_dashboard_base/data_source/mana_config";
import { _t } from "@web/core/l10n/translation";

let BaseModel = defaultModel.extend({

    defaults: {
        ...defaultModel.prototype.defaults,

        // config
        has_config: true,
        auto_load_config: true,
        copyable: true,

        template_category: undefined,

        // fetch data options
        fetch_data: true,
        fetch_model_data: true,
        fetch_sql_data: true,
        fetch_model_method_data: true,
        fetch_json_data: true,
        fetch_code_data: true,
        get_previous_data: false,

        // toolbar
        toolbar_config: { 'edit_config': true },

        time_range_sensitive: false,
        search_sensitive: false,

        mulit_source: false,
        config_model: 'mana_dashboard.config',
        config_form_res_id: 'mana_dashboard.config',
        config_class: Config,

        has_script: true,
        disable_children: false,
        disable_first_child: false,

        enable_drill_down: false,

        // set the default template
        dynamic_default_template: false,

        // use parent config
        use_parent_config: false,

        // extra domain
        extra_domain: [],

        css_libs: [],
        js_libs: [],
    },

    get_dashboard() {
        let config = this.em.getConfig();
        let dashboard = config.dashboard;
        return dashboard;
    },

    is_preview() {
        let config = this.em.getConfig();
        let preview = config.preview;
        return preview;
    },

    get_fetch_options() {
        return {
            fetch_data: this.get('fetch_data'),
            fetch_model_data: this.get('fetch_model_data'),
            fetch_sql_data: this.get('fetch_sql_data'),
            fetch_model_method_data: this.get('fetch_model_method_data'),
            fetch_json_data: this.get('fetch_json_data'),
            fetch_code_data: this.get('fetch_code_data'),
            get_previous_data: this.get('get_previous_data'),
        }
    },

    initialize() {

        // initalize
        defaultModel.prototype.initialize.apply(this, arguments);

        // gen a template id
        this.set('qweb_template_id', `qweb_template_${this.cid}`);

        // gen a demo template id
        this.set('qweb_demo_template_id', `qweb_demo_template_${this.cid}`);

        let dashboard = this.get_dashboard();
        let env = dashboard.env;
        this.set('env', env);

        // check dashboard loaded
        let is_preview = this.is_preview();

        let editor_ready = false;
        if (!is_preview) {
            editor_ready = dashboard.is_editor_ready && dashboard.is_editor_ready();
        }

        // check if is clone
        let isClone = this.opt && this.opt.isClone;
        if (!isClone) {
            if (editor_ready || is_preview || this.get('is_search')) {
                this.set('editor_ready', true);
                this._auto_reload_config();
            }
        } else {
            this.clone_config();
        }

        // bind events
        this._bind_events();

        // css libs
        this.ensure_libs();

        // disable children
        if (this.get('disable_children')) {
            this.disable_children();
        } else {
            // just not send to children
            this.set(
                'send_to_children',
                _.extend(this.get('send_to_children') || {}, {
                    draggable: false,
                    droppable: false,
                    selectable: false,
                    hoverable: false,
                    highlightable: false,
                }));
        }
    },

    _auto_reload_config() {
        // auto reloaded 
        if (this.get('auto_reloaded')) {
            return;
        }
        this.set('auto_reloaded', true, { silent: true });
        // config id
        let config_id = this.get('attributes').config_id;
        let auto_load_config = this.get('auto_load_config');
        if (config_id && auto_load_config) {
            this._load_config(parseInt(config_id));
        }
    },

    set_extra_domain(extra_domain) {
        this.set('extra_domain', extra_domain);
    },

    set_extra_info(extra_info) {
        this.set('extra_info', extra_info || {});
    },

    get_group_name() {
        let parent = this.parent();
        // get parent search group
        if (parent) {
            return parent.get_group_name();
        }
        return this.get('group_name');
    },

    _bind_events() {

        // listen to config change
        this.listenTo(this, 'change:config', this._on_config_change);

        // search_infos
        this.listenTo(this, 'change:search_infos', this.reload_config);

        // config id change
        this.listenTo(this, 'change:attributes:config_id', this._on_config_id_change);

        // template_id
        this.listenTo(this, 'change:template_external_id', this._on_template_id_change);

        // linked_info
        this.listenTo(this, 'change:linked_context', this._on_linked_context_change);

        // extra domain
        this.listenTo(this, 'change:extra_domain', this.reload_config);

        // extra info
        this.listenTo(this, 'change:extra_info', this.reload_config);

        let env = this.get('env');
        let bus = env.bus;

        // mana dashboard sorter:drag:start
        this.em.on('sorter:drag:start', this._on_drag_start, this);

        // sorter:drag:end
        this.em.on('sorter:drag:end', this._on_drag_end, this);

        // mana_dashboard.do_search
        this.doSearch = this._do_search.bind(this);
        env.bus.addEventListener('mana_dashboard.notify_item_do_search', this.doSearch);

        // mana_dashboard.do_search
        this.doInitSearch = this._do_init_search.bind(this);
        env.bus.addEventListener('mana_dashboard.notify_item_init_search', this.doInitSearch);

        // linked block change
        this.onLinkedBlockChanged = this._on_linked_block_changed.bind(this);
        env.bus.addEventListener(
            'mana_dashboard.linked_block_changed', this.onLinkedBlockChanged);

        // reload config
        this.onForceReloadConfig = this._on_force_reload_config.bind(this);
        env.bus.addEventListener(
            'mana_dashboard.force_reload_config', this.onForceReloadConfig);

        // mana_dashboard.timer.reload_config
        this.onTimerReloadConfig = this._on_timer_reload_config.bind(this);
        env.bus.addEventListener(
            'mana_dashboard.timer.reload_config', this.onTimerReloadConfig);

        // mana_dashboard.editor_ready
        this.onEditorReady = this._on_editor_ready.bind(this);
        env.bus.addEventListener('mana_dashboard.editor_ready', this.onEditorReady);

        // mana_dashboard.init_config
        this.onInitConfig = this._on_init_config.bind(this);
        env.bus.addEventListener('mana_dashboard.init_config', this.onInitConfig);

        // mana_dashboard.config_theme_changed
        this.onConfigThemeChanged = this._on_config_theme_changed.bind(this);
        env.bus.addEventListener('mana_dashboard.config_theme_changed', this.onConfigThemeChanged);

        // mana_dashboard.notify_item_query_data
        this.doQueryData = this._do_query_data.bind(this);
        env.bus.addEventListener('mana_dashboard.notify_item_query_data', this.doQueryData);

        // mana_dashboard.config_ready
        this.onConfigReady = this._on_config_ready.bind(this);
        env.bus.addEventListener('mana_dashboard.config_ready', this.onConfigReady);
    },

    /**
     * @returns {mana_dashboard.dashboard}
     */
    _on_config_ready() {
        if (this.is_preview()) {
            return;
        }
        let depend_config_ids = this.get('depend_config_ids') || [];
        let all_depend_config_ready = this.get('all_depend_config_ready');
        if (all_depend_config_ready) {
            return;
        }
        if (depend_config_ids.length == 0) {
            return;
        }
        let dashboard = this.get_dashboard();
        if (dashboard.is_all_depend_config_ready(depend_config_ids)) {
            this.set('all_depend_config_ready', true);
        }
    },

    _on_editor_ready() {
        this.set('editor_ready', true, { silent: true });
        // need to reload config
        this._auto_reload_config();
    },

    is_editor_ready() {
        return this.get('editor_ready');
    },

    _un_bind_events() {

        let env = this.get('env');
        
        // mana_dashboard.do_search
        env.bus.removeEventListener('mana_dashboard.notify_item_do_search', this.doSearch);

        // mana_dashboard.do_search
        env.bus.removeEventListener('mana_dashboard.notify_item_init_search', this.doInitSearch);

        // linked block change
        env.bus.removeEventListener('mana_dashboard.linked_block_changed', this.onLinkedBlockChanged);

        // reload config
        env.bus.removeEventListener('mana_dashboard.force_reload_config', this.onForceReloadConfig);

        // mana_dashboard.timer.reload_config
        env.bus.removeEventListener('mana_dashboard.timer.reload_config', this.onTimerReloadConfig);

        // mana_dashboard.editor_ready
        env.bus.removeEventListener('mana_dashboard.editor_ready', this.onEditorReady);

        // mana_dashboard.init_config
        env.bus.removeEventListener('mana_dashboard.init_config', this.onInitConfig);

        // mana_dashboard.config_theme_changed
        env.bus.removeEventListener('mana_dashboard.config_theme_changed', this.onConfigThemeChanged);

        // mana_dashboard.notify_item_query_data
        env.bus.removeEventListener('mana_dashboard.notify_item_query_data', this.doQueryData);

        // mana_dashboard.config_ready
        env.bus.removeEventListener('mana_dashboard.config_ready', this.onConfigReady);
    },

    _on_drag_start() {
        this.set('is_dragging', true);
    },

    _on_drag_end() {
        this.set('is_dragging', false);
    },

    ensure_libs() {
        return assets.loadBundle({
            jsLibs: this.get('js_libs'),
            cssLibs: this.get('css_libs'),
        });
    },

    _on_timer_reload_config(event) {
        let timer_props = event.detail;
        let config_id = this.get('attributes').config_id;
        config_id = parseInt(config_id);
        let targets = timer_props.targets || [];
        if (targets.length == 0 || targets.indexOf(config_id) >= 0) {
            this.reload_config();
        }
    },

    /**
     * dynamic default template, use this as the default template next time
     */
    _on_template_id_change: function () {

        let template_external_id = this.get('template_external_id');
        if (!template_external_id) {
            return;
        }
        let dynamic_default_template = this.get('dynamic_default_template');
        if (dynamic_default_template) {
            let component_type = this.get('type');
            this.trigger_up('mana_dashboard.change_default_template', {
                component_type: component_type,
                template_external_id: template_external_id,
            });
        }
    },

    disable_children() {

        let callback = (parent) => {
            let children = parent.get('components');
            if (children.length > 0) {
                children.each((child) => {

                    // disable
                    child.set('selectable', false);
                    child.set('draggable', false);
                    child.set('droppable', false);
                    child.set('hoverable', false);
                    child.set('highlightable', false);

                    child.removeAttributes([
                        'draggable', 'droppable', 'selectable', 'hoverable', 'highlightable'])

                    child.set('sendToChildren', {
                        draggable: false,
                        droppable: false,
                        selectable: false,
                        hoverable: false,
                        highlightable: false,
                    });

                    // check has children
                    if (child.get('components').length > 0) {
                        callback(child);
                    }
                });
            }
        }

        callback(this);

        // set send to children
        this.set(
            'sendToChildren',
            _.extend(this.get('sendToChildren') || {}, {
                draggable: false,
                droppable: false,
                selectable: false,
                hoverable: false,
                highlightable: false,
            }));

        this.set('disable_children', true);
    },

    _on_init_config(event) {
        let dashboard_id = event.detail;
        let config_id = this.get('attributes').config_id;
        if (config_id) {
            return;
        }

        if (!this.get('has_config')) {
            return;
        }

        let config_model = this.get('config_model');
        let template = this.get('attributes').template || false;
        if (!template) {
            return
        }
        return this._rpc({
            "model": 'mana_dashboard.any_config',
            "method": "create_config",
            "args": [dashboard_id, config_model, {
                'template': template,
            }],
        }).then((result) => {
            this.addAttributes({ 'config_id': result.config_id });
            this.removeAttributes(['template']);
        });
    },

    _on_linked_context_change() {
        this.reload_config();
    },

    _on_force_reload_config(event) {
        let editor = event.detail;
        // only reload config when the editor is the same
        if (editor == this.em.get('Editor')) {
            this.reload_config();
        }
    },

    get_qweb_template_id() {
        return this.get('qweb_template_id');
    },

    get_qweb_demo_template_id() {
        return this.get('qweb_demo_template_id');
    },

    _on_config_id_change() {
        let config_id = this.get_config_id();
        if (config_id) {
            this._load_config(config_id);
        }
    },

    _on_linked_block_changed(event) {
        let info = event.detail;
        let linked_config_ids = info.linked_config_ids
        let config_id = this.get_config_id()
        if (linked_config_ids.indexOf(config_id) != -1) {
            let linked_context = {
                $linked_field: info.category,
                $linked_value: info.value,
            }
            this.set('linked_context', linked_context);
        }
    },

    /**
     * get model by id
     * @param {*} id 
     * @returns 
     */
    get_model_by_id(id) {
        // check start with #
        if (id.indexOf('#') != 0) {
            id = '#' + id;
        }
        let item = this.$(id)
        if (item.length > 0) {
            let $el = grapesjs.$(item[0]);
            return $el.data('model');
        }
        return null;
    },

    get_context() {

        // normal context
        let context = {
            default_config_id: this.get_config_id(),
            default_any_config_id: this.get_config_id(),
        }

        // drill down context
        let drill_down_context = this.get('drill_down_context');
        if (drill_down_context) {
            context = _.extend(context, drill_down_context);
        }

        // linked action context
        let linked_context = this.get('linked_context');
        if (linked_context) {
            context = _.extend(context, linked_context);
        }

        // extra domain
        let extra_domain = this.get('extra_domain');
        if (extra_domain) {
            context = _.extend(context, {
                extra_domain: extra_domain,
            });
        }

        // extra info
        let extra_info = this.get('extra_info');
        if (extra_info) {
            context = _.extend(context, {
                extra_info: extra_info,
            });
        }

        return context;
    },

    _load_config(config_id, options = {remove_old_styles: false }) {

        this.set('loading_config', true);
        let fetch_option = this.get_fetch_options();
        if (options) {
            fetch_option = Object.assign(fetch_option, options);
        }

        let search_infos = this.get('search_infos') || [];
        fetch_option.search_infos = search_infos;

        this.rpc({
            model: 'mana_dashboard.any_config',
            method: 'get_config',
            args: [config_id, fetch_option],
            context: this.get_context(),
        }, options).then((result) => {

            this.set('loading_config', false);

            // reload config if failed
            if (!result) {
                this.set('load_config_failed', true);
                return;
            }

            // custom props
            let custom_props = result.custom_props || '{}';
            let config = result.ref_config || '{}';

            // theme info
            let theme_info = config.theme_info;
            if (theme_info) {
                theme_info = JSON.parse(theme_info);
                let theme = theme_info.theme;
                let theme_name = this.get_theme_name();
                this.set('theme_name', theme_name, { silent: true });
                this.set('theme', theme, { silent: true });
                echarts.registerTheme(theme_name, theme);
            }

            // set the props
            this.parse_custom_props(custom_props);

            // add a timestamp to force update
            result.timestamp = new Date().getTime();

            // force rerender if template changed
            let old_config = this.get('config');
            if (old_config || config.template) {

                // if the template id changed, we need to reset the components
                let new_template = config.template || '';
                new_template = new_template.trim();
                let old_template = old_config && old_config.template || '';
                old_template = old_template.trim();

                if (old_template && new_template != old_template) {
                    this.components().reset();
                }
            }

            // set time stamp to config
            config.timestamp = new Date().getTime();
            let ConfigClass = this.get('config_class') || Config;
            this.set('config', new ConfigClass(config));

            if (this.is_preview()) {
                return
            } else {
                // notify editor config ready
                this.em.trigger('mana_dashboard.config_ready', this);

                // depends ready
                let depend_config_ids = config.depend_config_ids || [];
                this.set('depend_config_ids', depend_config_ids);

                // all depend config ready
                let dashboard = this.get_dashboard();
                if (dashboard && dashboard.is_all_depend_config_ready(depend_config_ids)) {
                    this._on_all_depend_config_ready();
                }
            }
        })
    },

    _on_all_depend_config_ready() {
        this.set('all_depend_config_ready', true);
    },

    /**
     * get config id
     * @returns 
     */
    get_config_id() {
        let config_id = this.get('attributes').config_id;
        return parseInt(config_id);
    },

    /**
     * reload config
     * @returns 
     */
    reload_config(clear_style = false) {
        let config_id = this.get_config_id();
        if (!config_id) {
            return;
        }
        if (clear_style) {
            this.set('clear_style', clear_style, {
                'silent': true,
            });
        }
        this._load_config(parseInt(config_id));
    },

    /**
     * clone config
     * @returns 
     */
    clone_config() {
        let config_id = this.get_config_id();
        if (!config_id) {
            return;
        }
        // remove config id
        let custom_config_infos = this.get_custom_config_infos();
        this.removeAttributes(['config_id', 'form_trait_id']);
        this._rpc({
            model: 'mana_dashboard.any_config',
            method: 'clone_config',
            args: [config_id, custom_config_infos],
        }).then((result) => {
            this.addAttributes({ 'config_id': result.config_id });
            let custom_config_infos = result.custom_config_infos || [];
            for (let i = 0; i < custom_config_infos.length; i++) {
                let info = custom_config_infos[i];
                this.set('attributes', {
                    [info.key]: info.res_id,
                });
            }
            this.reload_config();
        });
    },

    /**
     * rewrite this method to parse config
     * @param {*} config 
     */
    parse_custom_props(config) { },

    /**
     * rewrite this method to get config
     */
    get_custom_props() { },

    /**
     * get custom config info
     */
    get_custom_config_infos() {
        return [];
    },

    /**
     * 
     * @param  {...any} args 
     * @returns 
     */
    get_default_props() { },

    get_dashboard_id() {
        let dashboard = this.get_dashboard();
        return dashboard.dashboard_id;
    },

    rpc(...args) {
        return this._rpc(...args);
    },

    _rpc(...args) {
        let dashboard = this.get_dashboard();
        if (!dashboard) {
            return Promise.reject();
        }
        return dashboard._rpc.apply(dashboard, args);
    },

    trigger_up(msg, data) {
        let dashboard = this.get_dashboard();
        if (!dashboard) {
            return;
        }
        return dashboard.trigger_up(msg, {
            data: data,
        });
    },

    do_action(...args) {
        let dashboard = this.get_dashboard();
        if (!dashboard) {
            return;
        }
        return dashboard.do_action(...args);
    },

    /**
     * query data, just for preview data
     * @param  {...any} args 
     */
    async _do_query_data(event) {
        let data = event.detail;

        let env = this.get('env');
        if (!env.inDialog) {
            return;
        }

        // check config id
        let any_config_id = data.any_config_id;
        let config_id = this.get_config_id();
        let data_source_id = data.data_source_id;
        if (!config_id) {
            return;
        }

        // check config id
        if (any_config_id != config_id) {
            return;
        }

        // get fetch options
        let fetch_option = {
            fetch_data: true,
            fetch_model_data: true,
            fetch_sql_data: true,
            fetch_model_method_data: true,
            fetch_json_data: true,
            fetch_code_data: true,
            get_previous_data: true,
            data_source_id: data_source_id,
        }
        let search_infos = this.get('search_infos') || [];
        fetch_option.search_infos = search_infos;

        // get dashboard
        let dashboard = this.get_dashboard();
        let orm = dashboard.orm;
        let result = await orm.call('mana_dashboard.any_config', 'get_datas', [
            config_id, fetch_option], {context: this.get_context()});

        // trigger message
        env.bus.trigger('mana_dashboard.get_datas_result', {
            config_id: config_id,
            data_source_id: data_source_id,
            result: result,
        });
    },

    _do_init_search(event) {
        let search_groups = event.detail;
        let search = this._do_search(search_groups);
        if (search) {
            this.set('auto_reloaded', true)
        }
    },

    _do_search(event) {
        let search_groups = event.detail;

        if (!this.get('search_sensitive')) {
            return
        }

        let _search_groups = [];
        for (let key in search_groups) {
            let search_group = search_groups[key];
            let type = search_group.type || 'global';
            if (type != 'global') {
                let targets = search_group.targets || [];
                let config_id = this.get_config_id();
                if (targets.indexOf(config_id) == -1) {
                    continue;
                }
            }
            _search_groups.push(search_group);
        }
        
        // merge search infos
        let global_search_groups = _search_groups.filter((group) => {
            return group.type == 'global';
        });

        // sort by priority
        global_search_groups.sort((a, b) => {
            return a.priority - b.priority;
        });

        let local_search_groups = _search_groups.filter((group) => {
            return group.type != 'global';
        });

        // sort by priority
        local_search_groups.sort((a, b) => {
            return a.priority - b.priority;
        });

        let all_groups = global_search_groups.concat(local_search_groups)
        let search_infos = {};
        for (let i = 0; i < all_groups.length; i++) {
            let tmp_infos = all_groups[i].search_infos || [];
            for (let key in tmp_infos) {
                let search_info = tmp_infos[key];
                let type = search_info.type;
                if (type == 'datetime_range') {
                    let old_search_info = tmp_infos[key];
                    let old_start = moment(old_search_info.start);
                    let old_end = moment(old_search_info.end);
                    let new_start = moment(search_info.start);
                    let new_end = moment(search_info.end);
                    let start = old_start.isAfter(new_start) ? old_start : new_start;
                    let end = old_end.isAfter(new_end) ? new_end : old_end;
                    // need to add the offset ?
                    search_info.start = start.format('YYYY-MM-DD HH:mm:ss');
                    search_info.end = end.format('YYYY-MM-DD HH:mm:ss');
                }
                search_infos[key] = search_info;
            }
        }

        // convert to array
        let _search_infos = [];
        for (let key in search_infos) {
            _search_infos.push(search_infos[key]);
        }

        // set search infos to trigger reload config
        let old_search_info = this.get('search_infos') || {};
        this.set('search_infos', _search_infos, {
            'silent': true,
        });

        // check if search infos changed
        if (Object.keys(search_infos).length > 0 || Object.keys(old_search_info).length > 0) {
            this.reload_config();
            return true;
        }

        return false;
    },

    _on_config_change() {

        let config = this.get('config');

        // update styles
        this.set('styles', config.styles);

        // update demo template
        this.set('demo_template', config.demo_template);

        // update demo data
        this.set('demo_data', config.demo_data);

        // update template
        this.set('template', config.template);

        // update template_name
        this.set('template_external_id', config.raw_config.template_external_id);

        // update scripts
        if (this.get('has_script')) {

            // prepend a timestamp to force update
            let timestamp = new Date().getTime();
            let scripts = config.scripts || '';

            let default_scripts = config.default_scripts || '';
            this.set('default_scripts', default_scripts, {
                'silent': true,
            });

            scripts = `// var timestamp = ${timestamp};\r\n` + scripts;
            this._update_script(scripts, config.config_changed);
        }

        // disable children
        if (config.raw_config.disable_children) {
            this.disable_children();
        }
    },

    /**
     * update script
     * @param {*} scripts 
     */
    _update_script(scripts) {
        this.set('script', scripts, {
            'silent': true,
        });
        if (this.view) {
            this.view.updateScript(scripts);
        }
    },

    /**
     * for form trait
     * @returns 
     */
    save_custom_props() {
        let config_id = this.get_config_id();
        if (!config_id) {
            return;
        }
        let dashboard = this.get_dashboard();
        if (!dashboard) {
            return;
        }
        let custom_props = this.get_custom_props() || {};
        return dashboard._rpc({
            model: 'mana_dashboard.any_config',
            method: 'write',
            args: [[parseInt(config_id)], { custom_props: JSON.stringify(custom_props) }],
        });
    },

    disable_first_child() {
        let components = this.components();
        if (components.length == 0) {
            return;
        }
        let first_child = this.components().at(0);
        if (first_child) {
            first_child.set('selectable', false);
            first_child.set('draggable', false);
            first_child.set('hoverable', false);
            first_child.set('movable', false);
            first_child.removeAttributes(
                ['draggable', 'droppable', 'selectable', 'hoverable', 'highlightable'])
        }
    },

    execute_default_script() {
        if (this.get('is_destroyed')) {
            return;
        }
        let default_scripts = this.get('default_scripts');
        if (!default_scripts) {
            return;
        }
        this.set('script', default_scripts);
    },

    /**
     * add a edit field toolbar tutton here
     * axorlor
     */
    initToolbar() {
        defaultModel.prototype.initToolbar.apply(this, arguments);

        const tb = this.get('toolbar');
        // has config
        if (this.get('has_config')) {
            let toolbar_config = this.get('toolbar_config');
            if (toolbar_config.edit_config) {
                const tbExists = tb.some(item => item.command === 'edit_config');
                if (!tbExists) {
                    tb.unshift({
                        command: 'edit_config',
                        label: icons.edit_chart_svg,
                    });
                }
            }
        }

        // enabled drill down
        if (this.get('enable_drill_down')) {
            const drillDownExists = tb.some(item => item.command === 'drill_down');
            if (!drillDownExists) {
                // add edit chart button
                tb.unshift({
                    command: 'drill_down',
                    label: icons.drill_down_svg,
                });
            }
            this.set('toolbar', tb);
        }
    },

    async nextTick() {
        await new Promise((resolve) => window.requestAnimationFrame(resolve));
        await new Promise((resolve) => setTimeout(resolve));
    },
    
    get_env() {
        let dashboard = this.get_dashboard();
        return dashboard.get_env();
    },

    destroy() {
        defaultModel.prototype.destroy.apply(this, arguments);
        this.destroyed = true;
    },

    get_theme_name() {
        let name = 'config_theme_' + this.get_config_id();
        return name;
    },

    /**
     * config theme changed
     * @param {*} data 
     */
    _on_config_theme_changed(event) {
        let data = event.detail;
        let config_id = data.config_id;
        let theme_info = data.theme_info;
        let tmp_config_id = this.get_config_id();
        if (config_id == tmp_config_id) {
            let theme = theme_info.theme;
            let theme_name = this.get_theme_name();
            echarts.registerTheme(theme_name, theme);
            this.set('theme_name', theme_name);
            this.set('theme', theme);
        }
    },

    /**
     * remove styles
     */
    remove_styles() {
        const css = this.em.get('Editor').Css;
        const rules = css.getAll();
        let toRemove = css.getComponentRules(this, {
            include_sub: true
        });
        rules.remove(toRemove);
    }
});

let BaseView = defaultView.extend({

    init() {
        defaultView.prototype.init.apply(this, arguments);

        // interval
        this.interval_ids = {};
        this.time_out_ids = {};

        // listen to template change
        this.listenTo(this.model, 'change:template', this.update_template);
        // listen to demo template change
        this.listenTo(this.model, 'change:demo_template', this.update_demo_template);
        // listen to styles change
        this.listenTo(this.model, 'change:styles', this._onchange_styles);
        // listen to load config failed
        this.listenTo(this.model, 'load_config_failed', this._on_load_config_failed);
        // listen to theme change
        this.listenTo(this.model, 'change:theme', this._onchange_theme);
        // listen to all components ready
        this.listenTo(this.model, 'all_depend_config_ready', this._on_all_depend_config_ready);

        // demo template
        let demo_template = this.model.get('demo_template');
        if (demo_template) {
            this.update_demo_template();
        }

        // template
        let template = this.model.get('template');
        if (template) {
            this.update_template();
        }
    },

    events: {
        'mouseenter': '_on_mouseenter',
        'mouseleave': '_on_mouseleave',
    },

    getSession() {
        let dashboard = this.model.get_dashboard();
        return dashboard.getSession();
    },

    _on_load_config_failed() {
        this.$el.html('Load config failed');
    },

    in_edit_mode() {
        let dashboard = this.get_dashboard();
        return dashboard.get_editor_mode() == 'edit';
    },

    _on_mouseenter(event) {
        let config = this.model.get('config');
        if (!config) {
            return;
        }
        let drill_up = config.drill_up_config;
        if (!drill_up) {
            return;
        }
        this.update_drill_up(true);
    },

    _onchange_theme() {
        this.render();
    },

    _on_mouseleave(event) {
        let config = this.model.get('config');
        if (!config) {
            return;
        }
        let drill_up = config.drill_up_config;
        if (!drill_up) {
            return;
        }
        this.update_drill_up(false);
    },

    update_drill_up(visible) {
        let $drill_up = this.el.querySelector('.drill-up-arrow');
        if ($drill_up) {
            $drill_up.style.display = visible ? 'block' : 'none';
        } else {
            if (visible) {
                this.render_drill_up_arrow();
            }
        }
    },

    get_config_id() {
        let config_id = this.model.get('attributes').config_id;
        return parseInt(config_id);
    },

    get_dashboard() {
        let config = this.model.em.getConfig();
        let dashboard = config.dashboard || config.dashboard;
        return dashboard;
    },

    get_env() {
        let dashboard = this.get_dashboard();
        return dashboard.get_env();
    },

    get_dashboard_id() {
        let dashboard = this.get_dashboard();
        return dashboard.dashboard_id;
    },

    /**
     * change styles
     */
    _onchange_styles() {
        let clear_style = this.model.get('clear_style')
        if (clear_style) {
            this.model.set('clear_style', false);
            this.model.remove_styles();
        }
        let styles = this.model.get('styles') || '';
        styles = styles.trim();
        // check style
        if (styles && styles != '') {
            this.add_dynamic_style(styles);
        }
    },

    /**
     * wait for element to exist
     * @returns 
     */
    waitForElementToExist(el, callback) {

        let editor = this.model.em.get('Editor');
        let root = editor.Canvas.getBody();

        return new Promise(resolve => {

            if (document.body.contains(this.el)) {
                return resolve();
            }

            const observer = new MutationObserver(() => {
                if (document.body.contains(this.el)) {
                    resolve();
                    observer.disconnect();
                }
            });

            observer.observe(root, {
                subtree: true,
                childList: true,
            });
        });
    },

    trigger_up(msg, data) {
        let dashboard = this.get_dashboard();
        if (!dashboard) {
            return;
        }
        return dashboard.trigger_up(msg, {
            data: data,
        });
    },

    /**
     * add dynamic style
     * @param {*} style 
     */
    add_dynamic_style(style) {
        const Css = this.model.em.get('Editor').Css;
        let cssText = this.wrap_style(style);
        Css.addRules(cssText);
    },

    rpc(...args) {
        let dashboard = this.get_dashboard();
        return dashboard._rpc(...args);
    },

    _rpc(...args) {
        return this.rpc(...args);
    },

    do_action(...args) {
        let dashboard = this.get_dashboard();
        return dashboard.do_action(...args);
    },

    get_qweb_template_id() {
        return this.model.get_qweb_template_id();
    },

    get_custom_props() {
        return this.model.get('custom_props');
    },

    get_raw_config() {
        let config = this.model.get('config');
        if (config) {
            return config.raw_config;
        }
        return null;
    },

    get_config: function () {
        return this.model.get('config');
    },

    get_data_sources() {
        let config = this.get_config();
        if (config) {
            return config.get_data_sources();
        }
        return [];
    },

    get_data_source(index = 0) {
        let config = this.get_config();
        if (config) {
            if (config.data_source_count <= index) {
                return null;
            }
            return config.get_data_source(index);
        }
        return null;
    },

    /**
     * add dynamic style
     * @param {*} style 
     */
    add_custom_style(style) {
        // add style
        let style_id = `style_${this.model.ccid}`;
        let style_tag = document.getElementById(style_id);
        if (style_tag) {
            style_tag.remove();
        }
        if (!style_tag) {
            style_tag = document.createElement('style');
            style_tag.id = style_id;
        }
        if (style_tag.styleSheet) {
            style_tag.styleSheet.cssText = this.wrap_style(style);
        } else {
            style_tag.innerHTML = this.wrap_style(style);
        }
        document.getElementsByTagName('head')[0].appendChild(style_tag);
    },

    /**
     * need test
     * @param {*} events 
     */
    extend_events(events) {
        this.events = _.extend({}, this.events, events);
        this.delegateEvents();
    },

    /**
     * wrap style, add a id to style tag
     */
    wrap_style(style) {
        // as the current moment, the id may be null
        let ccid = this.model.ccid;
        style = style.replace(/[^\}]*\{/g, function (match) {
            let selector = match.replace('{', '').replace('}', '').trim();
            // split by comma
            selector = selector.split(',').map((item) => {
                // remove comment
                item = item.replace(/\/\*.*\*\//g, '');
                // remove // comment
                item = item.replace(/\/\/.*/g, '');
                // check begin with &
                if (item.trim().startsWith('&')) {
                    return `#${ccid}${item.trim().replace('&', '')}`;
                } else {
                    return `#${ccid} ${item.trim()}`;
                }
            }).join(',');
            return `${selector} {`;
        });
        return style;
    },

    /**
     * remove template
     */
    remove_template() {

        let app = renderToString.app;
        let rawTemplates = app.rawTemplates;

        //
        let qweb_template_id = this.model.get_qweb_template_id();
        if (rawTemplates[qweb_template_id]) {
            rawTemplates[qweb_template_id];
        }

        // demo template
        let qweb_demo_template_id = this.model.get_qweb_demo_template_id();
        if (rawTemplates[qweb_demo_template_id]) {
            delete rawTemplates[qweb_demo_template_id];
        }
    },

    removed() {
        this.model.set('is_destroyed', true);

        this.remove_template();
        this.model._un_bind_events();

        this.clear_time_outs();
        this.clear_intervals();

        defaultView.prototype.removed.apply(this, arguments);
    },

    render_drill_up_arrow() {
        let config = this.model.get('config');
        let drill_up_config = config.drill_up_config;
        let $drill_up_arrow = $('<div class="drill-up-arrow"><i class="fa fa-arrow-up"></i></div>');
        $drill_up_arrow.click(() => {
            this.trigger_up('mana_dashboard.drill_up', {
                config_id: drill_up_config[0],
                model: this.model,
            });
        });
        this.$el.append($drill_up_arrow);
    },

    async nextTick() {
        await new Promise((resolve) => window.requestAnimationFrame(resolve));
        await new Promise((resolve) => setTimeout(resolve));
    },

    /**
     * has template
     * @returns {
     */
    has_template() {
        let template = this.model.get('template');
        if (!template || template.trim() == '') {
            return false;
        }
        return true;
    },

    _update_template(qweb_template_id, template) {

        template =  template? template.trim() : null;
        if (!template) {
            return;
        }

        // check has <template> tag
        if (template.indexOf('<template') == -1) {
            template = `<?xml version="1.0" encoding="UTF-8"?>
            <templates id="template" xml:space="preserve">
                    <t t-name="${qweb_template_id}">${template}</t>
            </templates>`;
        } else {
            // get the first template id, so it could call other template
            let template_id_match = template.match(/t-name="([^"]*)"/);
            if (template_id_match) {
                qweb_template_id = template_id_match[1];
            }
        }

        let app = renderToString.app;
        let rawTemplates = app.rawTemplates;

        if (rawTemplates[qweb_template_id]) {
            delete rawTemplates[qweb_template_id];
        }

        try {
            app.addTemplates(template);
        } catch (e) {
            let error_message = e.message;
            let error_template = `
            <?xml version="1.0" encoding="UTF-8"?>
                <templates id="template" xml:space="preserve">
                    <t t-name="${qweb_template_id}"><div class="alert alert-danger">${error_message}</div></t>
                </templates>
            `;
            app.addTemplates(error_template);
        }
    },

    /**
     * format template
     */
    update_template() {
        // check qweb aready exist
        let template = this.model.get('template') || '';
        template = template.trim();
        if (!template || template == '') {
            return;
        }
        let qweb_template_id = this.model.get_qweb_template_id();
        this._update_template(qweb_template_id, template);
    },

    /**
     * format demo template
     */
    update_demo_template() {
        let template = this.model.get('demo_template');
        if (!template) {
            return;
        }
        template = template? template.trim() : null;
        if (!template || template == '') {
            return
        }
        let qweb_demo_template_id = this.model.get_qweb_demo_template_id();
        this._update_template(qweb_demo_template_id, template);
    },

    _execute_script(script) {

        if (!script) {
            return;
        }

        let script_execute_mode = this.model.get('script_execute_mode');
        if (script_execute_mode == 'immediately') {
            try {
                let func = new Function([], script);
                func.apply(this);
            } catch (error) {
                console.log(`Error when execute script: ${error}`);
            }
        }
    },

    set_time_out(name, func, time) {
        // check if it is exist
        if (this.time_out_ids[name]) {
            clearTimeout(this.time_out_ids[name]);
        }
        let timeout_id = setTimeout(func, time);
        this.time_out_ids[name] = timeout_id;
        return timeout_id;
    },

    clear_time_outs() {
        for (let name in this.time_out_ids) {
            clearTimeout(this.time_out_ids[name]);
        }
        this.time_out_ids = {};
    },

    clear_time_out(name) {
        if (this.time_out_ids[name]) {
            clearTimeout(this.time_out_ids[name]);
            delete this.time_out_ids[name];
        }
    },

    set_interval(name, func, time) {
        // check if it is exist
        if (this.interval_ids[name]) {
            clearInterval(this.interval_ids[name]);
        }
        let interval_id = setInterval(func, time);
        this.interval_ids[name] = interval_id;
        return interval_id;
    },

    clear_intervals() {
        for (let name in this.interval_ids) {
            clearInterval(this.interval_ids[name]);
        }
        this.interval_ids = {};
    },

    clear_interval(name) {
        if (this.interval_ids[name]) {
            clearInterval(this.interval_ids[name]);
            delete this.interval_ids[name];
        }
    },

    get_editor_config() {
        return this.model.em.getConfig();
    },

    get_editor_mode() {
        let config = this.model.em.getConfig();
        let editor_mode = config.editor_mode;
        return editor_mode;
    },

    is_all_depend_config_ready() {
        return this.model.get('all_depend_config_ready');
    },

    has_depend_configs() {
        let depend_config_ids = this.model.get('depend_config_ids') || [];
        if (depend_config_ids.length > 0) {
            return true;
        }
        return false;
    },

    /**
     * on all depends ready
     */
    _on_all_depend_config_ready() {
        // render again
        this.render();
    },

    /**
     * get model by id
     * @param {*} model_id 
     */
    get_model_by_id(model_id) {
        // get wrapper, need test
        let wrapper = this.model.em.getWrapper();
        let $el = wrapper.view.$el;
        if (!model_id.startsWith('#')) {
            model_id = '#' + model_id;
        }
        let $item = $el.find(model_id);
        if ($item.length == 0) {
            return;
        }
        let model = $item.data('model');
        return model;
    },

    ensure_libs() {
        return this.model.ensure_libs();
    },

    get_marquee_elements() {
        let $marquee = $(this.el).find('.marquee');
        if (!$marquee.length) {
            $marquee = $(this.el);
        }
        return $marquee;
    },

    get_marquee_trait() {
        let model = this.model;
        while (model && !model.is('marquee')) {
            model = model.parent();
        }
        if (model) {
            return model.get('form_trait');
        }
        return {};
    },

    marquee() {
        this.ensure_libs().then(() => {
            let dashboard = this.get_dashboard();
            if (dashboard.is_prevew_widget()) {
                return;
            }
            let marquee_elements = this.get_marquee_elements();
            let mode = dashboard.get_mode();
            if (mode == 'view') {

                // set the height for marquee
                let height = marquee_elements.height();
                marquee_elements.css('height', height);

                // set display to block
                marquee_elements.css('display', 'block');

                // get form trait from parent
                let form_trait = this.get_marquee_trait();
                marquee_elements.liMarquee('destroy');
                marquee_elements.liMarquee(form_trait);
            } else {
                marquee_elements.liMarquee('destroy');
            }
        });
    }
});

export const BlockBase = {
    BaseModel,
    BaseView
}
