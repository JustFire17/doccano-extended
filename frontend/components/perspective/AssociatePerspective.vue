<template>
  <v-dialog :value="dialog" max-width="500px" @input="updateDialog">
    <v-card>
      <v-card-title class="headline">
        {{ hasAssociatedPerspective ? 'Dissociate Perspective' : 'Associate Perspective' }}
      </v-card-title>
      <v-card-text>
        <div v-if="hasAssociatedPerspective">
          <p>Current Perspective:</p>
          <v-card outlined class="pa-3 mb-4">
            <strong>{{ currentPerspective.name }}</strong>
          </v-card>
        </div>
        <v-select
          v-else
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
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="red" text @click="closeDialog">Cancel</v-btn>
        <v-btn 
          color="primary" 
          @click="hasAssociatedPerspective ? dissociate() : associate()"
        >
          {{ hasAssociatedPerspective ? 'Dissociate' : 'Associate' }}
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
    },
    currentPerspective: {
      type: Object,
      default: () => null
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
    hasAssociatedPerspective(): boolean {
      return !!this.currentPerspective
    },
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
    async associate() {
      if (!this.selectedPerspective) return
      this.isLoading = true
      try {
        await this.$emit('associate', this.selectedPerspective)
        this.closeDialog()
      } catch (error) {
        console.error('Error associating perspective:', error)
        alert('Error associating perspective. Please try again.')
      } finally {
        this.isLoading = false
      }
    },
    async dissociate() {
      this.isLoading = true
      try {
        await this.$emit('dissociate')
        this.closeDialog()
      } catch (error) {
        console.error('Error dissociating perspective:', error)
        alert('Error dissociating perspective. Please try again.')
      } finally {
        this.isLoading = false
      }
    }
  }
})
</script>