bl_info = {
    "name": "Sims4 Bone & Weight X-Mirror Renamer",
    "author": "copilot / mmd-riko",
    "version": (1, 1, 2),
    "blender": (3, 0, 0),
    "location": "3D View > Sidebar > S4 Rename",
    "description": "Convert TheSims4-style bone names to Blender x-mirror-friendly names and revert back. Also renames vertex groups. Supports multiple languages (English, Japanese, and others).",
    "category": "Rigging",
}

import bpy
import re
import json

MAP_PROP = "sim4_rename_map"
TEMP_SUFFIX = "__tmp_ren__"

# Localization dictionary (multiple languages)
# Keys used by the addon. English and Japanese preserved; additional languages added.
TEXTS = {
    "en": {
        "panel_title": "Sims4 Naming",
        "active_required": "Active Armature required",
        "convert_button": "Convert to X-Mirror Names",
        "revert_button": "Revert to Original Names",
        "processing": "Processing details:",
        "remove_b_prefix": "- Remove leading 'b__' and trim underscores",
        "convert_side": "- Detect L/R and convert to .L/.R suffix",
        "center_keep": "- Center bones kept as-is",
        "error_not_armature": "Active object is not an armature. Please select an armature.",
        "info_no_targets": "No bones found to convert (already converted or naming differs).",
        "error_conversion": "Error during conversion: {err}",
        "info_converted": "Converted {bones} bones. Vertex groups changed: {vgs}. Use Revert to restore.",
        "error_no_mapping": "No saved conversion mapping found on this armature.",
        "error_revert": "Error during revert: {err}",
        "info_reverted": "Revert complete. Bones: {bones}. Vertex groups changed: {vgs}.",
        "pref_label": "S4 Rename Preferences",
        "pref_language": "Language",
        "lang_auto": "Auto (use Blender language)",
        "lang_en": "English",
        "lang_ja": "日本語 (Japanese)",
    },
    "ja": {
        "panel_title": "Sims4 命名",
        "active_required": "アクティブなアーマチュアが必要です",
        "convert_button": "Xミラー用に変換",
        "revert_button": "元の命名に戻す",
        "processing": "処理内容",
        "remove_b_prefix": "- 先頭の 'b__' を除去し、'_' をトリム",
        "convert_side": "- L / R を検出して .L / .R サフィックスに変換",
        "center_keep": "- 中央ボーンはそのまま",
        "error_not_armature": "アクティブオブジェクトがアーマチュアではありません。アーマチュアを選択してください。",
        "info_no_targets": "変換対象のボーンが見つかりませんでした（既に変換済み、または命名規則が異なる可能性があります）。",
        "error_conversion": "変換中にエラー: {err}",
        "info_converted": "ボーン名を {bones} 件変換しました。頂点グループの変更: {vgs} 件。元に戻すには Revert を使用してください。",
        "error_no_mapping": "このアーマチュアには保存された変換マッピングがありません。",
        "error_revert": "リバート中にエラー: {err}",
        "info_reverted": "リバート完了。ボーン数: {bones}。頂点グループの変更: {vgs} 件。",
        "pref_label": "S4 Rename 設定",
        "pref_language": "言語",
        "lang_auto": "自動（Blender の言語設定に従う）",
        "lang_en": "English",
        "lang_ja": "日本語",
    },
    # Spanish
    "es": {
        "panel_title": "Nomenclatura Sims4",
        "active_required": "Se requiere un armature activo",
        "convert_button": "Convertir a nombres X-Mirror",
        "revert_button": "Revertir a nombres originales",
        "processing": "Detalles del proceso:",
        "remove_b_prefix": "- Eliminar prefijo 'b__' y recortar guiones bajos",
        "convert_side": "- Detectar L/R y convertir a sufijo .L/.R",
        "center_keep": "- Huesos centrales se mantienen",
        "error_not_armature": "El objeto activo no es un armature. Seleccione un armature.",
        "info_no_targets": "No se encontraron huesos para convertir (ya convertidos o nombre distinto).",
        "error_conversion": "Error durante la conversión: {err}",
        "info_converted": "Convertidos {bones} huesos. Grupos de vértices cambiados: {vgs}. Use Revert para restaurar.",
        "error_no_mapping": "No se encontró un mapeo de conversión guardado en este armature.",
        "error_revert": "Error durante la reversión: {err}",
        "info_reverted": "Reversión completa. Huesos: {bones}. Grupos de vértices cambiados: {vgs}.",
        "pref_label": "Preferencias S4 Rename",
        "pref_language": "Idioma",
        "lang_auto": "Auto (usar idioma de Blender)",
        "lang_en": "English",
        "lang_ja": "日本語",
    },
    # French
    "fr": {
        "panel_title": "Nommage Sims4",
        "active_required": "Armature active requise",
        "convert_button": "Convertir pour X-Mirror",
        "revert_button": "Revenir aux noms d'origine",
        "processing": "Détails du traitement :",
        "remove_b_prefix": "- Supprimer le préfixe 'b__' et tronquer les underscores",
        "convert_side": "- Détecter L/R et convertir en suffixe .L/.R",
        "center_keep": "- Les os centraux sont conservés",
        "error_not_armature": "L'objet actif n'est pas une armature. Veuillez sélectionner une armature.",
        "info_no_targets": "Aucun os à convertir trouvé (déjà converti ou nommage différent).",
        "error_conversion": "Erreur lors de la conversion : {err}",
        "info_converted": "Converti {bones} os. Groupes de vertex modifiés : {vgs}. Utilisez Revert pour restaurer.",
        "error_no_mapping": "Aucune table de conversion enregistrée pour cette armature.",
        "error_revert": "Erreur lors de la restauration : {err}",
        "info_reverted": "Restauration terminée. Os : {bones}. Groupes de vertex modifiés : {vgs}.",
        "pref_label": "Préférences S4 Rename",
        "pref_language": "Langue",
        "lang_auto": "Auto (utiliser la langue de Blender)",
        "lang_en": "English",
        "lang_ja": "日本語",
    },
    # German
    "de": {
        "panel_title": "Sims4 Benennung",
        "active_required": "Aktives Armature erforderlich",
        "convert_button": "Für X-Mirror konvertieren",
        "revert_button": "Auf Originalnamen zurücksetzen",
        "processing": "Verarbeitungsdetails:",
        "remove_b_prefix": "- Führendes 'b__' entfernen und Unterstriche trimmen",
        "convert_side": "- L/R erkennen und in .L/.R Suffix umwandeln",
        "center_keep": "- Zentrale Bones bleiben unverändert",
        "error_not_armature": "Das aktive Objekt ist keine Armature. Bitte wählen Sie eine Armature aus.",
        "info_no_targets": "Keine zu konvertierenden Bones gefunden (bereits konvertiert oder andere Namenskonvention).",
        "error_conversion": "Fehler während der Konvertierung: {err}",
        "info_converted": "{bones} Bones konvertiert. Vertex-Gruppen geändert: {vgs}. Zum Wiederherstellen Revert verwenden.",
        "error_no_mapping": "Keine gespeicherte Konvertierungszuordnung für diese Armature gefunden.",
        "error_revert": "Fehler beim Zurücksetzen: {err}",
        "info_reverted": "Zurücksetzen abgeschlossen. Bones: {bones}. Vertex-Gruppen geändert: {vgs}.",
        "pref_label": "S4 Rename Einstellungen",
        "pref_language": "Sprache",
        "lang_auto": "Auto (Blender Sprache verwenden)",
        "lang_en": "English",
        "lang_ja": "日本語",
    },
    # Chinese (Simplified)
    "zh": {
        "panel_title": "Sims4 命名",
        "active_required": "需要选中骨架（Armature）",
        "convert_button": "转换为 X 镜像 名称",
        "revert_button": "恢复为原始名称",
        "processing": "处理详情：",
        "remove_b_prefix": "- 移除前缀 'b__' 并修剪下划线",
        "convert_side": "- 检测 L/R 并转换为 .L/.R 后缀",
        "center_keep": "- 中央骨骼保持不变",
        "error_not_armature": "活动对象不是骨架。请选中一个骨架。",
        "info_no_targets": "未找到可转换的骨骼（可能已转换或命名不同）。",
        "error_conversion": "转换时出错：{err}",
        "info_converted": "已转换 {bones} 个骨骼。顶点组更改：{vgs} 个。使用 Revert 恢复。",
        "error_no_mapping": "在此骨架上未找到保存的转换映射。",
        "error_revert": "恢复时出错：{err}",
        "info_reverted": "恢复完成。骨骼：{bones}。顶点组更改：{vgs}。",
        "pref_label": "S4 Rename 设置",
        "pref_language": "语言",
        "lang_auto": "自动（使用 Blender 语言）",
        "lang_en": "English",
        "lang_ja": "日本語",
    },
    # Portuguese
    "pt": {
        "panel_title": "Nomenclatura Sims4",
        "active_required": "Armature ativo necessário",
        "convert_button": "Converter para nomes X-Mirror",
        "revert_button": "Reverter para nomes originais",
        "processing": "Detalhes do processamento:",
        "remove_b_prefix": "- Remover prefixo 'b__' e aparar underscores",
        "convert_side": "- Detectar L/R e converter para sufixo .L/.R",
        "center_keep": "- Ossos centrais mantidos",
        "error_not_armature": "O objeto ativo não é um armature. Por favor selecione um armature.",
        "info_no_targets": "Nenhum osso encontrado para converter (já convertido ou nome diferente).",
        "error_conversion": "Erro durante a conversão: {err}",
        "info_converted": "Convertidos {bones} ossos. Grupos de vértices alterados: {vgs}. Use Revert para restaurar.",
        "error_no_mapping": "Nenhum mapeamento de conversão salvo encontrado neste armature.",
        "error_revert": "Erro durante a reversão: {err}",
        "info_reverted": "Reversão concluída. Ossos: {bones}. Grupos de vértices alterados: {vgs}.",
        "pref_label": "Preferências S4 Rename",
        "pref_language": "Idioma",
        "lang_auto": "Auto (usar idioma do Blender)",
        "lang_en": "English",
        "lang_ja": "日本語",
    },
    # Russian
    "ru": {
        "panel_title": "Именование Sims4",
        "active_required": "Требуется активная арматура",
        "convert_button": "Преобразовать для X-Mirror",
        "revert_button": "Восстановить оригинальные имена",
        "processing": "Детали обработки:",
        "remove_b_prefix": "- Удалить префикс 'b__' и обрезать подчеркивания",
        "convert_side": "- Обнаружить L/R и конвертировать в суффикс .L/.R",
        "center_keep": "- Центральные кости оставляются",
        "error_not_armature": "Активный объект не является арматурой. Пожалуйста, выберите арматуру.",
        "info_no_targets": "Не найдены кости для преобразования (возможно уже преобразованы или другое именование).",
        "error_conversion": "Ошибка при преобразовании: {err}",
        "info_converted": "Преобразовано {bones} костей. Изменено групп вершин: {vgs}. Используйте Revert для восстановления.",
        "error_no_mapping": "Сохраненная карта преобразования не найдена для этой арматуры.",
        "error_revert": "Ошибка при восстановлении: {err}",
        "info_reverted": "Восстановление завершено. Костей: {bones}. Изменено групп вершин: {vgs}.",
        "pref_label": "Настройки S4 Rename",
        "pref_language": "Язык",
        "lang_auto": "Авто (использовать язык Blender)",
        "lang_en": "English",
        "lang_ja": "日本語",
    },
    # Korean
    "ko": {
        "panel_title": "Sims4 명명",
        "active_required": "활성 아마추어(Armature)가 필요합니다",
        "convert_button": "X-미러용으로 변환",
        "revert_button": "원래 이름으로 복원",
        "processing": "처리 내용:",
        "remove_b_prefix": "- 앞의 'b__' 제거 및 밑줄 트림",
        "convert_side": "- L/R 감지 후 .L/.R 접미사로 변환",
        "center_keep": "- 중앙 본은 그대로 유지",
        "error_not_armature": "활성 객체가 아마추어가 아닙니다. 아마추어를 선택하세요.",
        "info_no_targets": "변환할 본을 찾을 수 없습니다(이미 변환되었거나 명명 규칙이 다를 수 있음).",
        "error_conversion": "변환 중 오류: {err}",
        "info_converted": "{bones} 개 본을 변환했습니다. 버텍스 그룹 변경: {vgs} 개. Revert로 복원하세요.",
        "error_no_mapping": "이 아마추어에 저장된 변환 맵이 없습니다.",
        "error_revert": "복원 중 오류: {err}",
        "info_reverted": "복원 완료. 본 수: {bones}. 버텍스 그룹 변경: {vgs}.",
        "pref_label": "S4 Rename 설정",
        "pref_language": "언어",
        "lang_auto": "자동(Blender 언어 사용)",
        "lang_en": "English",
        "lang_ja": "日本語",
    },
    # Italian
    "it": {
        "panel_title": "Denominazione Sims4",
        "active_required": "Armatura attiva richiesta",
        "convert_button": "Converti per X-Mirror",
        "revert_button": "Ripristina nomi originali",
        "processing": "Dettagli di elaborazione:",
        "remove_b_prefix": "- Rimuovi prefisso 'b__' e trim degli underscore",
        "convert_side": "- Rileva L/R e converti in suffisso .L/.R",
        "center_keep": "- Le ossa centrali vengono mantenute",
        "error_not_armature": "L'oggetto attivo non è un'armatura. Seleziona un'armatura.",
        "info_no_targets": "Nessun osso trovato da convertire (già convertito o nomenclatura diversa).",
        "error_conversion": "Errore durante la conversione: {err}",
        "info_converted": "Convertite {bones} ossa. Gruppi di vertici modificati: {vgs}. Usa Revert per ripristinare.",
        "error_no_mapping": "Nessuna mappatura di conversione salvata trovata in questa armatura.",
        "error_revert": "Errore durante il ripristino: {err}",
        "info_reverted": "Ripristino completato. Ossa: {bones}. Gruppi di vertici modificati: {vgs}.",
        "pref_label": "Preferenze S4 Rename",
        "pref_language": "Lingua",
        "lang_auto": "Auto (usa lingua di Blender)",
        "lang_en": "English",
        "lang_ja": "日本語",
    },
}

def get_addon_language_setting():
    """
    Returns language code like 'en','ja','es',... based on addon preference or Blender language when set to AUTO.
    """
    lang_choice = "AUTO"
    try:
        addon = bpy.context.preferences.addons.get(__name__)
        if addon:
            prefs = addon.preferences
            lang_choice = prefs.language
    except Exception:
        lang_choice = "AUTO"

    # Direct mapping from preference selection to TEXTS keys
    if lang_choice == "EN":
        return "en"
    if lang_choice == "JA":
        return "ja"
    if lang_choice == "ES":
        return "es"
    if lang_choice == "FR":
        return "fr"
    if lang_choice == "DE":
        return "de"
    if lang_choice == "ZH":
        return "zh"
    if lang_choice == "PT":
        return "pt"
    if lang_choice == "RU":
        return "ru"
    if lang_choice == "KO":
        return "ko"
    if lang_choice == "IT":
        return "it"

    # AUTO -> inspect Blender language setting
    try:
        bl_lang = bpy.context.preferences.view.language
        if bl_lang:
            bl = bl_lang.lower()
            if bl.startswith("ja"):
                return "ja"
            if bl.startswith("es"):
                return "es"
            if bl.startswith("fr"):
                return "fr"
            if bl.startswith("de"):
                return "de"
            if bl.startswith("zh"):
                return "zh"
            if bl.startswith("pt"):
                return "pt"
            if bl.startswith("ru"):
                return "ru"
            if bl.startswith("ko"):
                return "ko"
            if bl.startswith("it"):
                return "it"
    except Exception:
        pass
    return "en"

def t(key):
    lang = get_addon_language_setting()
    return TEXTS.get(lang, TEXTS["en"]).get(key, TEXTS["en"].get(key, key))

def normalize_name_remove_b_and_unders(name: str) -> str:
    if name.startswith("b__"):
        name = name[3:]
    name = name.strip("_")
    return name

def detect_side_and_base(name: str):
    # If already contains .L or .R suffix
    m = re.match(r'^(.*)\.(L|R)$', name)
    if m:
        base = m.group(1)
        return base, m.group(2)

    # Leading L_ or R_
    m = re.match(r'^([LR])_(.*)$', name)
    if m:
        return m.group(2).strip("_"), m.group(1)

    # Middle _L_ or _R_
    m = re.search(r'_(L|R)_', name)
    if m:
        side = m.group(1)
        base = name.replace("_" + side + "_", "_")
        base = base.strip("_")
        return base, side

    # Trailing _L or _R
    m = re.search(r'_(L|R)$', name)
    if m:
        side = m.group(1)
        base = name[: - (len(m.group(0)))]
        base = base.strip("_")
        return base, side

    return name.strip("_"), None

def to_xmirror_name(orig_name: str) -> str:
    name = normalize_name_remove_b_and_unders(orig_name)
    base, side = detect_side_and_base(name)
    if side is None:
        return base
    return f"{base}.{side}"

def build_conversion_map(bones):
    mapping = {}
    for b in bones:
        orig = b.name
        new = to_xmirror_name(orig)
        if new != orig:
            mapping[orig] = new
    return mapping

def rename_bones(arm_obj, mapping):
    ctx = bpy.context
    prev_mode = ctx.mode
    # Make armature active
    ctx.view_layer.objects.active = arm_obj
    for obj in ctx.view_layer.objects:
        obj.select_set(False)
    arm_obj.select_set(True)
    # Enter edit mode
    try:
        bpy.ops.object.mode_set(mode='EDIT')
    except RuntimeError:
        pass

    arm = arm_obj.data
    edit_bones = arm.edit_bones

    # Collision checks
    new_names = list(mapping.values())
    if len(set(new_names)) != len(new_names):
        raise RuntimeError(t("error_conversion").format(err="Name collision among targets."))

    existing_names = set(b.name for b in arm.bones)
    for target in new_names:
        if target in existing_names and target not in mapping.keys():
            raise RuntimeError(t("error_conversion").format(err=f"Target name '{target}' already exists and is not part of rename mapping."))

    # Two-pass renaming to avoid collisions
    temp_map = {}
    for orig, new in mapping.items():
        eb = edit_bones.get(orig)
        if eb is None:
            continue
        tmp = new + TEMP_SUFFIX
        if tmp in edit_bones:
            tmp = tmp + "_x"
        eb.name = tmp
        temp_map[tmp] = orig

    for tmp, orig in temp_map.items():
        eb = edit_bones.get(tmp)
        if eb:
            final = mapping[orig]
            eb.name = final

    # Restore mode
    try:
        bpy.ops.object.mode_set(mode=prev_mode)
    except Exception:
        pass

def rename_vertex_groups_for_armature(arm_obj, mapping):
    renamed = 0
    for obj in bpy.data.objects:
        if obj.type != 'MESH' or not obj.vertex_groups:
            continue
        uses = False
        for mod in obj.modifiers:
            if mod.type == 'ARMATURE' and mod.object == arm_obj:
                uses = True
                break
        if not uses:
            continue
        # rename vertex groups (watch for collision)
        vg_names = {g.name for g in obj.vertex_groups}
        for g in list(obj.vertex_groups):
            if g.name in mapping:
                target = mapping[g.name]
                if target in vg_names and target != g.name:
                    raise RuntimeError(f"Vertex group name collision on object '{obj.name}': target '{target}' already exists.")
                g.name = target
                renamed += 1
    return renamed

def store_mapping_on_armature(arm_obj, mapping):
    try:
        arm_obj[MAP_PROP] = json.dumps(mapping)
    except Exception as e:
        raise RuntimeError("Failed to store mapping on armature: " + str(e))

def load_mapping_from_armature(arm_obj):
    if MAP_PROP not in arm_obj:
        return None
    try:
        mapping = json.loads(arm_obj[MAP_PROP])
        return mapping
    except Exception:
        return None

def clear_mapping_on_armature(arm_obj):
    if MAP_PROP in arm_obj:
        try:
            del arm_obj[MAP_PROP]
        except Exception:
            pass

class S4_OT_ConvertNames(bpy.types.Operator):
    bl_idname = "s4.rename_to_xmirror"
    bl_label = "Convert (S4->Xmirror)"
    bl_description = "Convert TheSims4-style bone names to Blender x-mirror-friendly names and rename related vertex groups"

    def execute(self, context):
        arm_obj = context.active_object
        if not arm_obj or arm_obj.type != 'ARMATURE':
            self.report({'ERROR'}, t("error_not_armature"))
            return {'CANCELLED'}
        bones = arm_obj.data.bones
        mapping = build_conversion_map(bones)
        if not mapping:
            self.report({'INFO'}, t("info_no_targets"))
            return {'CANCELLED'}
        try:
            rename_bones(arm_obj, mapping)
            renamed_vg = rename_vertex_groups_for_armature(arm_obj, mapping)
            store_mapping_on_armature(arm_obj, mapping)
        except Exception as e:
            self.report({'ERROR'}, t("error_conversion").format(err=str(e)))
            return {'CANCELLED'}
        self.report({'INFO'}, t("info_converted").format(bones=len(mapping), vgs=renamed_vg))
        return {'FINISHED'}

class S4_OT_RevertNames(bpy.types.Operator):
    bl_idname = "s4.revert_names"
    bl_label = "Revert (Xmirror->S4)"
    bl_description = "Revert bone names and vertex groups to the original names saved during conversion"

    def execute(self, context):
        arm_obj = context.active_object
        if not arm_obj or arm_obj.type != 'ARMATURE':
            self.report({'ERROR'}, t("error_not_armature"))
            return {'CANCELLED'}
        mapping = load_mapping_from_armature(arm_obj)
        if not mapping:
            self.report({'ERROR'}, t("error_no_mapping"))
            return {'CANCELLED'}
        reverse = {v: k for k, v in mapping.items()}
        if not reverse:
            self.report({'ERROR'}, t("error_no_mapping"))
            return {'CANCELLED'}
        try:
            rename_bones(arm_obj, reverse)
            renamed_vg = rename_vertex_groups_for_armature(arm_obj, reverse)
            clear_mapping_on_armature(arm_obj)
        except Exception as e:
            self.report({'ERROR'}, t("error_revert").format(err=str(e)))
            return {'CANCELLED'}
        self.report({'INFO'}, t("info_reverted").format(bones=len(reverse), vgs=renamed_vg))
        return {'FINISHED'}

class S4_PT_Panel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "S4 Rename"
    bl_label = "S4 Rename"

    def draw(self, context):
        layout = self.layout
        # Localized panel title
        layout.label(text=t("panel_title"))
        col = layout.column(align=True)
        col.label(text=t("active_required"))
        # Single Convert button (localized)
        col.operator("s4.rename_to_xmirror", text=t("convert_button"), icon='SNAP_ON')
        # Revert button (localized)
        col.operator("s4.revert_names", text=t("revert_button"), icon='LOOP_BACK')
        col.separator()
        col.label(text=t("processing"))
        col.label(text=t("remove_b_prefix"))
        col.label(text=t("convert_side"))
        col.label(text=t("center_keep"))

class S4_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    language: bpy.props.EnumProperty(
        name="Language",
        items=(
            ("AUTO", "Auto", "Use Blender language preference"),
            ("EN", "English", "Force English UI"),
            ("JA", "日本語", "Force Japanese UI"),
            ("ES", "Español", "Force Spanish UI"),
            ("FR", "Français", "Force French UI"),
            ("DE", "Deutsch", "Force German UI"),
            ("ZH", "中文", "Force Chinese (Simplified) UI"),
            ("PT", "Português", "Force Portuguese UI"),
            ("RU", "Русский", "Force Russian UI"),
            ("KO", "한국어", "Force Korean UI"),
            ("IT", "Italiano", "Force Italian UI"),
        ),
        default="AUTO",
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text=t("pref_label"))
        row = layout.row()
        row.prop(self, "language", text=t("pref_language"))
        layout.label(text=t("lang_auto"))
        # Show sample language names
        layout.label(text=t("lang_en"))
        layout.label(text=t("lang_ja"))

classes = (
    S4_OT_ConvertNames,
    S4_OT_RevertNames,
    S4_PT_Panel,
    S4_AddonPreferences,
)

def register():
    for c in classes:
        bpy.utils.register_class(c)

def unregister():
    for c in reversed(classes):
        bpy.utils.unregister_class(c)

if __name__ == "__main__":
    register()