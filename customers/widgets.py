from django import forms
from django.utils.safestring import mark_safe
import json


class CustomFileInput(forms.FileInput):
    """
    Custom file input widget with drag-and-drop support and image preview.
    Uses Alpine.js for interactivity and Tailwind CSS for styling.
    """

    def __init__(self, attrs=None, accept=None):
        default_attrs = {
            'class': 'hidden',
            'x-ref': 'fileInput',
            '@change': 'handleFileSelect($event)',
        }
        if accept:
            default_attrs['accept'] = accept
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)

    def render(self, name, value, attrs=None, renderer=None):
        # Build the input attributes
        if attrs is None:
            attrs = {}
        attrs = {**self.attrs, **attrs}

        # Build attrs string
        attrs_str = ' '.join([f'{k}="{v}"' for k, v in attrs.items()])

        # Get current file info
        current_file = value if value else None
        current_file_name = getattr(value, 'name', '') if value else ''
        current_file_url = getattr(value, 'url', '') if value else ''

        # Use a unique ID for this widget instance
        widget_id = f"fi_{name.replace('-', '_')}"

        html = f'''
<script>
function fileInputData_{widget_id}() {{
    return {{
        isDragging: false,
        previewUrl: {"'" + current_file_url + "'" if current_file_url else "null"},
        fileName: '',
        fileSize: '',
        currentFile: {"'" + str(current_file) + "'" if current_file else "null"},
        currentFileName: {"'" + current_file_name + "'" if current_file_name else "null"},
        handleFileSelect(event) {{
            const file = event.target.files[0];
            if (file) {{ this.processFile(file); }}
        }},
        handleDrop(event) {{
            this.isDragging = false;
            const file = event.dataTransfer.files[0];
            if (file) {{
                const input = this.$refs.fileInput;
                const dataTransfer = new DataTransfer();
                dataTransfer.items.add(file);
                input.files = dataTransfer.files;
                this.processFile(file);
            }}
        }},
        processFile(file) {{
            this.fileName = file.name;
            this.fileSize = this.formatFileSize(file.size);
            this.currentFile = null;
            if (file.type.startsWith('image/')) {{
                const reader = new FileReader();
                reader.onload = (e) => {{ this.previewUrl = e.target.result; }};
                reader.readAsDataURL(file);
            }}
        }},
        clearFile() {{
            this.previewUrl = null;
            this.fileName = '';
            this.fileSize = '';
            this.currentFile = null;
            this.$refs.fileInput.value = '';
        }},
        formatFileSize(bytes) {{
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
        }}
    }};
}}
</script>
<div x-data="fileInputData_{widget_id}()" class="mt-1">
    <!-- Hidden file input -->
    <input type="file" name="{name}" {attrs_str}>

    <!-- Drop Zone -->
    <div
        @click="$refs.fileInput.click()"
        @dragover.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
        @drop.prevent="handleDrop($event)"
        :class="isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-gray-400'"
        class="relative border-2 border-dashed rounded-lg p-6 cursor-pointer transition-colors duration-200"
    >
        <!-- Preview Area -->
        <div x-show="previewUrl || currentFile" class="flex flex-col items-center gap-4">
            <!-- Image Preview -->
            <div x-show="previewUrl" class="relative">
                <img :src="previewUrl" alt="Preview" class="max-h-48 rounded-lg border border-gray-200">
                <button
                    type="button"
                    @click.stop="clearFile()"
                    class="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600 transition-colors"
                >
                    <svg class="size-4" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                </button>
            </div>

            <!-- Current File Info (when editing and no new file selected) -->
            <div x-show="!previewUrl && currentFile" class="flex items-center gap-2 text-sm text-gray-600">
                <svg class="size-4" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M9 12H15M9 16H15M17 21H7C5.89543 21 5 20.1046 5 19V5C5 3.89543 5.89543 3 7 3H12.5858C12.851 3 13.1054 3.10536 13.2929 3.29289L18.7071 8.70711C18.8946 8.89464 19 9.149 19 9.41421V19C19 20.1046 18.1046 21 17 21Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                <span x-text="currentFileName"></span>
            </div>

            <!-- File Info -->
            <div x-show="fileName" class="text-sm text-gray-600">
                <p x-text="fileName" class="font-medium"></p>
                <p x-show="fileSize" x-text="fileSize" class="text-xs text-gray-500"></p>
            </div>
        </div>

        <!-- Upload Prompt (shown when no file) -->
        <div x-show="!previewUrl && !currentFile" class="flex flex-col items-center gap-2 text-center">
            <svg class="size-10 text-gray-400" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M16 7L12 3M12 3L8 7M12 3V15M21 11V17.7992C21 18.9193 21 19.4794 20.782 19.9072C20.5903 20.2835 20.2843 20.5895 19.908 20.7812C19.4802 20.9992 18.9201 20.9992 17.8 20.9992H6.2C5.0799 20.9992 4.51984 20.9992 4.09202 20.7812C3.71569 20.5895 3.40973 20.2835 3.21799 19.9072C3 19.4794 3 18.9193 3 17.7992V11" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <div class="text-sm">
                <span class="text-blue-600 font-medium">לחץ להעלאה</span>
                <span class="text-gray-500">או גרור ושחרר קובץ</span>
            </div>
            <p class="text-xs text-gray-500">PNG, JPG, GIF עד 10MB</p>
        </div>
    </div>
</div>
'''
        return mark_safe(html)


class CustomSelect(forms.Select):
    """
    Custom select widget with search/filter functionality.
    Default variant: Clean styled dropdown.
    Type directly in the field to filter options.
    Supports dynamic option updates via Alpine.js integration.
    """

    def __init__(self, attrs=None, choices=(), allow_dynamic_options=False):
        default_attrs = {
            'class': 'hidden'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, choices=choices)
        self.allow_dynamic_options = allow_dynamic_options

    def render(self, name, value, attrs=None, renderer=None):
        if attrs is None:
            attrs = {}
        attrs = {**self.attrs, **attrs}

        # Build options list
        options = []
        for option_value, option_label in self.choices:
            # Skip empty choice
            if option_value == '':
                continue
            selected = str(option_value) == str(value) if value else False
            options.append({
                'value': str(option_value),
                'label': str(option_label),
                'selected': selected
            })

        # Get selected label
        selected_label = ''
        for opt in options:
            if opt['selected']:
                selected_label = opt['label']
                break

        # Check if this widget should support dynamic options (integration with parent Alpine.js)
        init_watcher = ''
        if self.allow_dynamic_options:
            # This allows parent Alpine.js component to control options and selected value
            init_watcher = f'''
            init() {{
                this.$watch('{name.replace('-', '_')}_options', (value) => {{
                    if (value) {{
                        this.options = value;
                    }}
                }});
                this.$watch('{name.replace('-', '_')}_selected', (value) => {{
                    if (value && value !== this.selectedValue) {{
                        this.updateSelection(value);
                    }}
                }});
            }},
            '''

        # Escape values for JavaScript
        js_selected_label = selected_label.replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"') if selected_label else ''
        js_value = str(value).replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"') if value else ''
        options_json = json.dumps(options)

        options_html = ''.join([f'<option value="{opt["value"]}" {"selected" if opt["selected"] else ""}>{opt["label"]}</option>' for opt in options])

        # Use a unique ID for this widget instance
        widget_id = f"cs_{name.replace('-', '_')}"

        html = f'''
<script type="text/javascript">
(function() {{
    window.customSelectData_{widget_id} = function() {{
        return {{
            {init_watcher}
            isOpen: false,
            searchQuery: '{js_selected_label}',
            selectedValue: '{js_value}',
            selectedLabel: '{js_selected_label}',
            highlightedIndex: -1,
            options: {options_json},
            get filteredOptions() {{
                if (!this.searchQuery || this.searchQuery.trim() === '') return this.options;
                const query = this.searchQuery.toLowerCase();
                return this.options.filter(opt => opt.label.toLowerCase().includes(query));
            }},
            openDropdown() {{ this.isOpen = true; this.highlightedIndex = -1; this.searchQuery = ''; }},
            closeDropdown() {{ this.isOpen = false; this.highlightedIndex = -1; if (!this.selectedValue) {{ this.searchQuery = ''; }} else {{ this.searchQuery = this.selectedLabel; }} }},
            selectOption(option) {{ this.selectedValue = option.value; this.selectedLabel = option.label; this.searchQuery = option.label; this.$refs.hiddenSelect.value = option.value; this.isOpen = false; this.$refs.hiddenSelect.dispatchEvent(new Event('change', {{ bubbles: true }})); }},
            navigateDown() {{ if (this.highlightedIndex < this.filteredOptions.length - 1) {{ this.highlightedIndex++; }} }},
            navigateUp() {{ if (this.highlightedIndex > 0) {{ this.highlightedIndex--; }} }},
            selectHighlighted() {{ if (this.highlightedIndex >= 0 && this.highlightedIndex < this.filteredOptions.length) {{ this.selectOption(this.filteredOptions[this.highlightedIndex]); }} }},
            clearSelection() {{ this.selectedValue = ''; this.selectedLabel = ''; this.searchQuery = ''; this.$refs.hiddenSelect.value = ''; this.$refs.hiddenSelect.dispatchEvent(new Event('change', {{ bubbles: true }})); }}{(',' if self.allow_dynamic_options else '')}
            {f"updateSelection(newValue) {{ const option = this.options.find(opt => opt.value === String(newValue)); if (option) {{ this.selectedValue = option.value; this.selectedLabel = option.label; this.searchQuery = option.label; this.$refs.hiddenSelect.value = option.value; }} }}" if self.allow_dynamic_options else ''}
        }};
    }};
}})();
</script>
<div x-data="window.customSelectData_{widget_id}()" class="relative" @click.outside="closeDropdown()">
    <!-- Hidden select input -->
    <select name="{name}" class="hidden" x-ref="hiddenSelect">
        <option value="">---------</option>
        {options_html}
    </select>

    <!-- Searchable input field -->
    <div class="relative">
        <input
            type="text"
            x-model="searchQuery"
            @focus="openDropdown()"
            @input="openDropdown()"
            @keydown.escape="closeDropdown()"
            @keydown.arrow-down.prevent="navigateDown()"
            @keydown.arrow-up.prevent="navigateUp()"
            @keydown.enter.prevent="selectHighlighted()"
            placeholder="בחר אפשרות..."
            class="input-field w-full"
            :class="selectedValue ? '' : ''"
            autocomplete="off"
        >
        <!-- Clear button -->
        <button
            x-show="selectedValue && !isOpen"
            type="button"
            @click.stop="clearSelection()"
            class="absolute left-9 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
        >
            <svg class="size-4" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </button>
        <!-- Dropdown arrow -->
        <div class="absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none">
            <svg class="size-4 transition-transform text-gray-400" :class="isOpen ? 'rotate-180' : ''" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M6 9L12 15L18 9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </div>
    </div>

    <!-- Dropdown menu -->
    <div
        x-show="isOpen"
        x-transition
        class="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-y-auto"
    >
        <template x-for="(option, index) in filteredOptions" :key="option.value">
            <button
                type="button"
                @click="selectOption(option)"
                @mouseenter="highlightedIndex = index"
                class="w-full px-4 py-2 text-right hover:bg-gray-100 flex items-center justify-between transition-colors"
                :class="{{
                    'bg-blue-50 text-blue-600': option.value === selectedValue,
                    'bg-gray-100': index === highlightedIndex && option.value !== selectedValue
                }}"
            >
                <span x-text="option.label"></span>
                <svg x-show="option.value === selectedValue" class="size-4" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M20 6L9 17L4 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </button>
        </template>
        <div x-show="filteredOptions.length === 0" class="px-4 py-3 text-sm text-gray-500 text-center">
            לא נמצאו תוצאות
        </div>
    </div>
</div>
'''
        return mark_safe(html)


class DynamicCustomSelect(forms.Select):
    """
    Custom searchable select widget for dynamically populated options.
    Used for payment service dropdown where options come from quote service line items.
    Integrates with JavaScript that updates options dynamically.
    """

    def __init__(self, attrs=None, choices=()):
        default_attrs = {
            'class': 'hidden'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, choices=choices)

    def render(self, name, value, attrs=None, renderer=None):
        if attrs is None:
            attrs = {}
        attrs = {**self.attrs, **attrs}

        # Use a unique ID for this widget instance
        widget_id = f"dcs_{name.replace('-', '_')}"

        # Escape value for JavaScript
        js_value = str(value).replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"') if value else ''

        html = f'''
<script type="text/javascript">
(function() {{
    window.dynamicCustomSelectData_{widget_id} = function() {{
        return {{
            isOpen: false,
            searchQuery: '',
            selectedValue: '{js_value}',
            selectedLabel: '',
            highlightedIndex: -1,
            options: [],
            get filteredOptions() {{
                if (!this.searchQuery || this.searchQuery.trim() === '') return this.options;
                const query = this.searchQuery.toLowerCase();
                return this.options.filter(opt => opt.label.toLowerCase().includes(query));
            }},
            init() {{
                // Update selected label from options on init
                this.updateSelectedLabel();
            }},
            updateSelectedLabel() {{
                const option = this.options.find(opt => opt.value === this.selectedValue);
                this.selectedLabel = option ? option.label : '';
                this.searchQuery = this.selectedLabel;
            }},
            openDropdown() {{ this.isOpen = true; this.highlightedIndex = -1; this.searchQuery = ''; }},
            closeDropdown() {{
                this.isOpen = false;
                this.highlightedIndex = -1;
                this.searchQuery = this.selectedLabel;
            }},
            selectOption(option) {{
                this.selectedValue = option.value;
                this.selectedLabel = option.label;
                this.searchQuery = option.label;
                this.$refs.hiddenSelect.value = option.value;
                this.isOpen = false;
                this.$refs.hiddenSelect.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }},
            navigateDown() {{ if (this.highlightedIndex < this.filteredOptions.length - 1) {{ this.highlightedIndex++; }} }},
            navigateUp() {{ if (this.highlightedIndex > 0) {{ this.highlightedIndex--; }} }},
            selectHighlighted() {{
                if (this.highlightedIndex >= 0 && this.highlightedIndex < this.filteredOptions.length) {{
                    this.selectOption(this.filteredOptions[this.highlightedIndex]);
                }}
            }},
            clearSelection() {{
                this.selectedValue = '';
                this.selectedLabel = '';
                this.searchQuery = '';
                this.$refs.hiddenSelect.value = '';
                this.$refs.hiddenSelect.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }},
            updateOptionsFromDOM() {{
                // Called by external JavaScript to update options from DOM select
                const selectElement = this.$refs.hiddenSelect;
                const newOptions = [];
                for (let i = 0; i < selectElement.options.length; i++) {{
                    const opt = selectElement.options[i];
                    if (opt.value) {{
                        newOptions.push({{
                            value: opt.value,
                            label: opt.textContent
                        }});
                    }}
                }}
                this.options = newOptions;
                this.updateSelectedLabel();
            }}
        }};
    }};
}})();
</script>
<div x-data="window.dynamicCustomSelectData_{widget_id}()" class="relative" @click.outside="closeDropdown()">
    <!-- Hidden select input (will be populated by JavaScript) -->
    <select name="{name}" class="hidden payment-service-select" x-ref="hiddenSelect">
        <option value="">בחר שירות</option>
    </select>

    <!-- Searchable input field -->
    <div class="relative">
        <input
            type="text"
            x-model="searchQuery"
            @focus="openDropdown()"
            @input="openDropdown()"
            @keydown.escape="closeDropdown()"
            @keydown.arrow-down.prevent="navigateDown()"
            @keydown.arrow-up.prevent="navigateUp()"
            @keydown.enter.prevent="selectHighlighted()"
            placeholder="בחר שירות..."
            class="input-field w-full"
            autocomplete="off"
        >
        <!-- Clear button -->
        <button
            x-show="selectedValue && !isOpen"
            type="button"
            @click.stop="clearSelection()"
            class="absolute left-9 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
        >
            <svg class="size-4" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </button>
        <!-- Dropdown arrow -->
        <div class="absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none">
            <svg class="size-4 transition-transform text-gray-400" :class="isOpen ? 'rotate-180' : ''" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M6 9L12 15L18 9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </div>
    </div>

    <!-- Dropdown menu -->
    <div
        x-show="isOpen"
        x-transition
        class="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-y-auto"
    >
        <template x-for="(option, index) in filteredOptions" :key="option.value">
            <button
                type="button"
                @click="selectOption(option)"
                @mouseenter="highlightedIndex = index"
                class="w-full px-4 py-2 text-right hover:bg-gray-100 flex items-center justify-between transition-colors"
                :class="{{
                    'bg-blue-50 text-blue-600': option.value === selectedValue,
                    'bg-gray-100': index === highlightedIndex && option.value !== selectedValue
                }}"
            >
                <span x-text="option.label"></span>
                <svg x-show="option.value === selectedValue" class="size-4" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M20 6L9 17L4 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </button>
        </template>
        <div x-show="filteredOptions.length === 0" class="px-4 py-3 text-sm text-gray-500 text-center">
            לא נמצאו תוצאות
        </div>
    </div>
</div>
'''
        return mark_safe(html)


class StatusSelect(forms.Select):
    """
    Custom select widget for status fields with color-coded pills.
    Shows status with appropriate styling based on status type.
    """

    # Status color mapping
    STATUS_COLORS = {
        # Lead statuses
        'new': 'info',
        'follow': 'alert',
        'quote': 'proccess',
        'won': 'success',
        'lost': 'danger',
        'trash': 'default',
        # Quote statuses
        'draft': 'info',
        'sent': 'proccess',
        # Project Statuses
        'open': 'info',
        'completed': 'success',
        'canceled': 'danger',
        'onHold': 'alert',
    }

    def __init__(self, attrs=None, choices=()):
        default_attrs = {
            'class': 'hidden'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs, choices=choices)

    def get_status_class(self, value):
        """Get the CSS class for a status value"""
        return self.STATUS_COLORS.get(str(value), 'default')

    def render(self, name, value, attrs=None, renderer=None):
        if attrs is None:
            attrs = {}
        attrs = {**self.attrs, **attrs}

        # Build options list with status classes
        options = []
        for option_value, option_label in self.choices:
            # Skip empty choice
            if option_value == '':
                continue
            selected = str(option_value) == str(value) if value else False
            options.append({
                'value': str(option_value),
                'label': str(option_label),
                'selected': selected,
                'statusClass': self.get_status_class(option_value)
            })

        # Get selected option
        selected_option = None
        for opt in options:
            if opt['selected']:
                selected_option = opt
                break

        selected_option_json = json.dumps(selected_option)
        options_json = json.dumps(options)

        # Use a unique ID for this widget instance
        widget_id = f"ss_{name.replace('-', '_')}"

        html = f'''
<script>
function statusSelectData_{widget_id}() {{
    return {{
        isOpen: false,
        searchQuery: '',
        selectedOption: {selected_option_json},
        highlightedIndex: -1,
        options: {options_json},
        get filteredOptions() {{
            if (!this.searchQuery || this.searchQuery.trim() === '') return this.options;
            const query = this.searchQuery.toLowerCase();
            return this.options.filter(opt => opt.label.toLowerCase().includes(query));
        }},
        openDropdown() {{ this.isOpen = true; this.highlightedIndex = -1; }},
        closeDropdown() {{ this.isOpen = false; this.highlightedIndex = -1; this.searchQuery = ''; }},
        selectOption(option) {{ this.selectedOption = option; this.$refs.hiddenSelect.value = option.value; this.isOpen = false; this.searchQuery = ''; this.$refs.hiddenSelect.dispatchEvent(new Event('change', {{ bubbles: true }})); }},
        navigateDown() {{ if (this.highlightedIndex < this.filteredOptions.length - 1) {{ this.highlightedIndex++; }} }},
        navigateUp() {{ if (this.highlightedIndex > 0) {{ this.highlightedIndex--; }} }},
        selectHighlighted() {{ if (this.highlightedIndex >= 0 && this.highlightedIndex < this.filteredOptions.length) {{ this.selectOption(this.filteredOptions[this.highlightedIndex]); }} }},
        clearSelection() {{ this.selectedOption = null; this.searchQuery = ''; this.$refs.hiddenSelect.value = ''; this.$refs.hiddenSelect.dispatchEvent(new Event('change', {{ bubbles: true }})); }}
    }};
}}
</script>
<div x-data="statusSelectData_{widget_id}()" class="relative" @click.outside="closeDropdown()">
    <!-- Hidden select input -->
    <select name="{name}" class="hidden" x-ref="hiddenSelect">
        <option value="">---------</option>
        {''.join([f'<option value="{opt["value"]}" {"selected" if opt["selected"] else ""}>{opt["label"]}</option>' for opt in options])}
    </select>

    <!-- Searchable input field -->
    <div class="relative">
        <input
            type="text"
            x-model="searchQuery"
            @focus="openDropdown()"
            @input="openDropdown()"
            @keydown.escape="closeDropdown()"
            @keydown.arrow-down.prevent="navigateDown()"
            @keydown.arrow-up.prevent="navigateUp()"
            @keydown.enter.prevent="selectHighlighted()"
            :placeholder="selectedOption ? '' : 'בחר סטטוס...'"
            class="input-field w-full"
            :class="selectedOption ? '' : ''"
            autocomplete="off"
        >
        <!-- Clear button -->
        <button
            x-show="selectedOption && !isOpen"
            type="button"
            @click.stop="clearSelection()"
            class="absolute left-9 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors z-10"
        >
            <svg class="size-4" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </button>
        <!-- Dropdown arrow -->
        <div class="absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none">
            <svg class="size-4 transition-transform text-gray-400" :class="isOpen ? 'rotate-180' : ''" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M6 9L12 15L18 9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        </div>
        <!-- Selected status pill overlay -->
        <div x-show="selectedOption && !isOpen" class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
            <span class="status-pill" :class="selectedOption?.statusClass" x-text="selectedOption?.label"></span>
        </div>
    </div>

    <!-- Dropdown menu -->
    <div
        x-show="isOpen"
        x-transition
        class="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-y-auto"
    >
        <template x-for="(option, index) in filteredOptions" :key="option.value">
            <button
                type="button"
                @click="selectOption(option)"
                @mouseenter="highlightedIndex = index"
                class="w-full px-4 py-2 text-right hover:bg-gray-100 flex items-center justify-between transition-colors"
                :class="{{
                    'bg-blue-50': option.value === selectedOption?.value,
                    'bg-gray-100': index === highlightedIndex && option.value !== selectedOption?.value
                }}"
            >
                <span class="status-pill" :class="option.statusClass" x-text="option.label"></span>
                <svg x-show="option.value === selectedOption?.value" class="size-4" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M20 6L9 17L4 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </button>
        </template>
        <div x-show="filteredOptions.length === 0" class="px-4 py-3 text-sm text-gray-500 text-center">
            לא נמצאו תוצאות
        </div>
    </div>
</div>
'''
        return mark_safe(html)
