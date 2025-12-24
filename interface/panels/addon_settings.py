import bpy


# ------------------------------------------------------------------------
# Operator: Relink UI (SAFE, minimal, no extra dependencies)
# ------------------------------------------------------------------------
class SN_OT_RelinkUI(bpy.types.Operator):
    bl_idname = "sn.relink_ui"
    bl_label = "Relink UI"
    bl_description = "Temporarily remove and recreate INTERFACE links in all Serpens node trees"
    bl_options = {"REGISTER"}  # keep minimal; remove UNDO to avoid oddities with links

    def execute(self, context):
        storage = []

        for tree in bpy.data.node_groups:
            # Your original condition, but guarded (some ID types don't support `"key" in tree`)
            is_sn = False
            try:
                is_sn = hasattr(tree, "is_sn") or ("is_sn" in tree)
            except Exception:
                is_sn = hasattr(tree, "is_sn")

            if not is_sn:
                continue

            links_to_save = []
            for l in list(tree.links):
                f_color = getattr(l.from_node, "node_color", "")
                t_color = getattr(l.to_node, "node_color", "")

                if f_color == "INTERFACE" or t_color == "INTERFACE":
                    links_to_save.append((l.from_socket, l.to_socket))
                    try:
                        tree.links.remove(l)
                    except Exception:
                        pass

            if links_to_save:
                storage.append((tree, links_to_save))

        for tree, saved_links in storage:
            for from_sock, to_sock in saved_links:
                try:
                    tree.links.new(from_sock, to_sock)
                except Exception:
                    pass

        self.report({"INFO"}, "Relink UI complete")
        return {"FINISHED"}


# ------------------------------------------------------------------------
# Panels (YOUR CODE + minimal additions only)
# ------------------------------------------------------------------------
class SN_PT_AddonSettingsPanel(bpy.types.Panel):
    bl_idname = "SN_PT_AddonSettingsPanel"
    bl_label = ""
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Serpens"
    bl_options = {"DEFAULT_CLOSED", "HEADER_LAYOUT_EXPAND"}
    bl_order = 8

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == "ScriptingNodesTree" and context.space_data.node_tree

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="Settings")
        layout.operator("wm.url_open", text="", icon="QUESTION", emboss=False).url = "https://joshuaknauber.notion.site/Workflow-Introduction-d235d03178124dc9b752088d75a25192"

    def draw(self, context):
        layout = self.layout
        sn = context.scene.sn

        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column(heading="General")
        col.prop(sn, "watch_script_changes")
        col.prop(sn, "show_graph_categories")
        col.prop(sn, "show_property_categories")
        col.prop(sn, "overwrite_variable_graph")
        col.prop(sn, "compile_on_load")

        layout.separator()
        col = layout.column(heading="Generated Code")
        col.prop(sn, "debug_code", text="Keep Code File")
        subcol = col.column()
        subcol.enabled = sn.debug_code
        subcol.prop(sn, "remove_duplicate_code")
        subcol.prop(sn, "format_code")

        layout.separator()
        col = layout.column(heading="Debug")
        col.prop(sn, "debug_compile_time", text="Log Compile Time")
        col.prop(sn, "debug_python_nodes")
        col.prop(sn, "debug_python_sockets")
        subrow = col.row()
        subrow.active = sn.debug_python_nodes or sn.debug_python_sockets
        subrow.prop(sn, "debug_selected_only")
        col.prop(sn, "debug_python_properties")

        # --------------------------------------------------
        # NEW: Debug -> Relink UI section + button
        # --------------------------------------------------
        box = layout.box()
        box.label(text="Relink UI", icon="FILE_REFRESH")
        box.operator("sn.relink_ui", text="Relink UI", icon="FILE_REFRESH")


class SN_PT_EasyBpyPanel(bpy.types.Panel):
    bl_idname = "SN_PT_EasyBpyPanel"
    bl_parent_id = "SN_PT_AddonSettingsPanel"
    bl_label = ""
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Serpens"
    bl_order = 0
    bl_options = {"HEADER_LAYOUT_EXPAND"}

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == "ScriptingNodesTree" and context.space_data.node_tree

    def draw_header(self, context):
        layout = self.layout
        layout.label(text="Easy BPY")
        layout.operator("wm.url_open", text="", icon="QUESTION", emboss=False).url = "https://joshuaknauber.notion.site/Easy-BPY-e3a894c7bf4c469389e6caa7640c3219"

    def draw(self, context):
        layout = self.layout
        sn = context.scene.sn

        layout.use_property_split = True
        layout.use_property_decorate = False

        if sn.easy_bpy_path:
            layout.label(text="Easy BPY installed", icon="CHECKMARK")
            layout.operator("sn.open_explorer", text="Open Install", icon="FILE_FOLDER").path = sn.easy_bpy_path
        else:
            layout.label(text="Easy BPY not installed", icon="CANCEL")
        layout.operator("wm.url_open", text="Documentation", icon="URL").url = "https://curtisholt.online/easybpy"