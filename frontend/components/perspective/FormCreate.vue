<template>
  <v-card>
    <v-card-title>Create Perspective</v-card-title>
    <v-card-text>
      <v-form ref="form" v-model="valid">
        <v-row>
          <v-col cols="12">
            <v-text-field
              :value="name"
              :rules="[rules.required, rules.counter]"
              label="Perspective Name"
              outlined
              required
              @input="$emit('update:name', $event)"
            />
          </v-col>
        </v-row>

        <v-divider class="my-4"></v-divider>
        <v-subheader>Perspective Items</v-subheader>

        <div v-for="(item, index) in items" :key="index" class="item-container">
          <v-card class="mb-4" outlined>
            <v-card-text>
              <v-row align="center">
                <v-col cols="11">
                  <div class="d-flex align-center mb-4">
                    <span class="text-h6">Item {{ index + 1 }}</span>
                  </div>
                  <v-row>
                    <v-col cols="6">
                      <v-text-field
                        v-model="item.name"
                        :rules="[rules.required, rules.duplicateName]"
                        label="Item Name"
                        outlined
                        required
                        @input="updateItems"
                      />
                    </v-col>
                    <v-col cols="6">
                      <v-select
                        v-model="item.type"
                        :items="dataTypes"
                        :rules="[rules.required]"
                        label="Type"
                        outlined
                        required
                        @change="onTypeChange($event, index)"
                      />
                    </v-col>
                  </v-row>

                  <v-row v-if="item.type === 'options'">
                    <v-col cols="12">
                      <v-text-field
                        v-model="item.options"
                        :rules="[rules.required, rules.optionsValidation]"
                        :label="item.name + ' Options'"
                        hint="Enter options separated by semicolons (;)"
                        persistent-hint
                        outlined
                        required
                        @input="updateItems"
                      >
                        <template #append>
                          <v-btn icon small @click="removeLastOption(index)">
                            <v-icon small>mdi-minus</v-icon>
                          </v-btn>
                        </template>
                      </v-text-field>
                    </v-col>
                  </v-row>
                </v-col>
                <v-col cols="1" class="d-flex justify-center align-center">
                  <v-btn
                    icon
                    color="error"
                    class="delete-btn"
                    @click="removeItem(index)"
                  >
                    <v-icon>mdi-trash-can</v-icon>
                  </v-btn>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </div>

        <v-row class="mt-4">
          <v-col cols="12">
            <v-btn color="primary" text @click="addItem">
              <v-icon left>mdi-plus</v-icon>
              Add Item
            </v-btn>
          </v-col>
        </v-row>

        <v-row>
          <v-col cols="12">
            <slot :valid="isFormValid" />
          </v-col>
        </v-row>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script lang="ts">
import Vue from 'vue'

interface PerspectiveItem {
  name: string;
  type: string;
  options: string;
}

interface Data {
  valid: boolean;
  items: PerspectiveItem[];
  dataTypes: string[];
  rules: {
    required: (v: string) => string | boolean;
    counter: (v: string) => string | boolean;
    duplicateName: (v: string) => string | boolean;
    optionsValidation: (v: string) => string | boolean;
  };
}

export default Vue.extend({
  props: {
    name: {
      type: String,
      required: true
    }
  },

  data(): Data {
    return {
      valid: false,
      items: [],
      dataTypes: ['number', 'string', 'yes/no', 'options'],
      rules: {
        required: (v: string) => !!v || 'This field is required',
        counter: (v: string) => (v && v.length <= 100) || 'Name must be less than 100 characters',
        duplicateName: (v: string) => {
          const items = this.$data.items as PerspectiveItem[];
          const count = items.filter((item: PerspectiveItem) => item.name === v).length;
          return count <= 1 || 'Item name must be unique';
        },
        optionsValidation: (v: string) => {
          if (!v || v.trim() === '') return 'Options field is required';
          const options = v.split(';').map(option => option.trim());
          if (options.length < 2) return 'Options must contain at least two values separated by ";"';
          if (options.includes('')) return 'Each option must contain a valid value';
          const uniqueOptions = new Set(options);
          if (uniqueOptions.size !== options.length) return 'Options must not contain duplicate values';
          return true;
        }
      }
    }
  },

  computed: {
    isFormValid(): boolean {
      return this.valid && this.items.length > 0 && this.items.every((item: PerspectiveItem) => {
        if (item.type === 'options') {
          return item.name && item.type && item.options;
        }
        return item.name && item.type;
      });
    }
  },

  methods: {
    addItem() {
      this.items.push({
        name: '',
        type: '',
        options: ''
      });
      this.updateItems();
    },

    removeItem(index: number) {
      if (index >= 0 && index < this.items.length) {
        this.items.splice(index, 1);
        this.$nextTick(() => {
          this.updateItems();
        });
      }
    },

    onTypeChange(value: string, index: number) {
      this.items[index].type = value;
      if (value !== 'options') {
        this.items[index].options = '';
      }
      this.updateItems();
    },

    removeLastOption(index: number) {
      const item = this.items[index];
      if (item.type === 'options' && item.options) {
        const options = item.options.split(';').map(opt => opt.trim());
        if (options.length > 2) {
          options.pop();
          item.options = options.join(';');
          this.updateItems();
        }
      }
    },

    updateItems() {
      this.$emit('update:items', this.items);
    }
  }
})
</script>

<style scoped>
.item-container {
  position: relative;
}

.item-container:not(:last-child) {
  margin-bottom: 16px;
}

.delete-btn {
  background-color: rgba(255, 0, 0, 0.1) !important;
}

.delete-btn:hover {
  background-color: rgba(255, 0, 0, 0.2) !important;
}
</style>