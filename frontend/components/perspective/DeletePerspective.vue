<template>
  <v-dialog :value="dialog" max-width="500px" @input="updateDialog">
    <v-card>
      <v-card-title class="headline">
        Delete Perspective
      </v-card-title>
      <v-card-text>
        <v-select
          v-model="selectedPerspective"
          :items="availablePerspectives"
          item-text="name"
          item-value="id"
          label="Select Perspective"
          :rules="[rules.required]"
          clearable
          :loading="!hasAvailablePerspectives"
          :disabled="!hasAvailablePerspectives"
        >
          <template #no-data>
            <v-list-item>
              <v-list-item-content>
                <v-list-item-title>
                  No perspectives available
                </v-list-item-title>
              </v-list-item-content>
            </v-list-item>
          </template>
        </v-select>
        <v-alert
          v-if="selectedPerspective"
          type="warning"
          class="mt-3"
        >
          Are you sure you want to delete this perspective? This action cannot be undone.
        </v-alert>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="red" text @click="closeDialog">Cancel</v-btn>
        <v-btn 
          color="error" 
          :disabled="!selectedPerspective"
          @click="deletePerspective"
        >
          Delete
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import Vue from 'vue'

export default Vue.extend({
  props: {
    dialog: Boolean,
    availablePerspectives: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      selectedPerspective: null,
      rules: {
        required: (v: any) => !!v || "Required"
      },
      isLoading: false
    }
  },
  computed: {
    hasAvailablePerspectives(): boolean {
      return this.availablePerspectives && this.availablePerspectives.length > 0
    }
  },
  methods: {
    updateDialog(value: boolean) {
      this.$emit('update:dialog', value)
    },
    closeDialog() {
      this.updateDialog(false)
      this.selectedPerspective = null
    },
    async deletePerspective() {
      if (!this.selectedPerspective) return
      this.isLoading = true
      try {
        await this.$emit('delete', this.selectedPerspective)
        this.closeDialog()
      } catch (error) {
        console.error('Error deleting perspective:', error)
        alert('Error deleting perspective. Please try again.')
      } finally {
        this.isLoading = false
      }
    }
  }
})
</script> 