<template>
  <v-card>
    <v-card-title class="text-h6">Fill Perspectives</v-card-title>
    <v-card-text>
      <v-alert v-if="!hasPerspective" type="warning">
        This project doesn't have an associated perspective set. Please ask an administrator to associate a perspective with this project.
      </v-alert>
      <v-form v-else ref="form" v-model="valid" :disabled="!isEditing">
        <v-row v-for="(perspective, index) in processedPerspectives" :key="index">
          <v-col cols="12" sm="6">
            <v-text-field
              v-if="perspective.type === 'string' && !perspective.options"
              v-model="formData[perspective.id]"
              :label="perspective.name"
              :rules="[rules.required]"
              outlined
            />
            <v-text-field
              v-else-if="perspective.type === 'number' && !perspective.options"
              v-model.number="formData[perspective.id]"
              :label="perspective.name"
              type="number"
              :rules="[rules.required]"
              outlined
            />
            <v-select
              v-else-if="perspective.type === 'yes/no'"
              v-model="formData[perspective.id]"
              :label="perspective.name"
              :items="['Yes', 'No']"
              :rules="[rules.required]"
              outlined
            />
            <v-select
              v-else-if="perspective.options"
              v-model="formData[perspective.id]"
              :label="perspective.name"
              :items="perspective.optionsArray"
              :rules="[rules.required]"
              outlined
            />
          </v-col>
        </v-row>
      </v-form>
    </v-card-text>
    <v-card-actions class="ps-4 pt-0">
      <v-btn v-if="!isEditing && hasPerspective" color="primary" class="text-capitalize" @click="checkAnnotationsAndEdit">
        Edit
      </v-btn>
      <v-btn
        v-show="isEditing"
        color="primary"
        :disabled="!valid || isSaving"
        class="mr-4 text-capitalize"
        @click="save"
      >
        Save
      </v-btn>
      <v-btn v-show="isEditing" :disabled="isSaving" class="text-capitalize" @click="cancel">
        Cancel
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script lang="ts">
import Vue from 'vue'
import { PerspectiveDTO } from '~/services/application/perspective/perspectiveData'

export default Vue.extend({
  layout: 'project',

  middleware: ['check-auth', 'auth', 'setCurrentProject'],

  data() {
    return {
      items: [] as PerspectiveDTO[],
      formData: {} as Record<string, any>,
      valid: false,
      isEditing: false,
      isSaving: false,
      hasPerspective: false,
      rules: {
        required: (v: string | number) => !!v || 'This field is required'
      }
    }
  },

  async fetch() {
    try {
      // First, get the current project to check if it has an associated perspective
      const currentProject = await this.$services.project.findById(this.projectId)
      this.hasPerspective = !!currentProject.perspective_associated
      
      // If the project has an associated perspective, fetch the perspectives
      if (this.hasPerspective) {
        try {
          this.items = await this.service.list(this.projectId)
          const values = await this.service.getFilledValues(this.projectId)
          for (const p of this.items) {
            this.$set(this.formData, p.id, values[p.id] || '')
          }
        } catch (perspectiveError) {
          console.error('Error loading perspectives:', perspectiveError)
          this.hasPerspective = false // Set to false if there's an error loading perspectives
          alert('Error loading perspectives. Please try again later.')
        }
      }
      
      this.isEditing = false
    } catch (error) {
      console.error('Error loading project:', error)
      this.hasPerspective = false // Ensure hasPerspective is false if there's any error
      alert('Error loading project. Please try again later.')
    }
  },

  computed: {
    projectId(): string {
      return this.$route.params.id
    },

    service(): any {
      return this.$services.perspective
    },

    processedPerspectives(): any[] {
      return this.items.map(perspective => ({
        ...perspective,
        optionsArray: perspective.options ? perspective.options.split(';').map(opt => opt.trim()) : []
      }))
    }
  },

  methods: {
    async checkAnnotationsAndEdit() {
      try {
        // Check if there are any examples in the project
        const examples = await this.$services.example.list(this.projectId, {
          limit: '100',
          offset: '0',
          q: '',
          isChecked: '',
          ordering: '-id'
        })
        
        if (examples.items && examples.items.length > 0) {
          // Check each example for annotations
          for (const example of examples.items) {
            const annotations = await this.$repositories.category.list(this.projectId, example.id)
            if (annotations && annotations.length > 0) {
              alert('You cannot edit perspectives after making annotations. Please delete your annotations first.')
              this.$router.push(`/projects/${this.projectId}/text-classification`)
              return
            }
          }
        }
        
        // If no annotations found in any example, allow editing
        this.isEditing = true
      } catch (error) {
        console.error('Error checking annotations:', error)
        alert('Error checking annotations. Please try again later.')
      }
    },
    
    cancel() {
      this.$fetch()
    },
    
    async save() {
      this.isSaving = true
      try {
        await this.service.fillPerspectives(this.projectId, this.formData)
        await this.$fetch()
        alert('Perspectives saved successfully')
      } catch (error) {
        console.error('Error saving perspectives:', error)
        alert('Error saving perspectives. Please try again later.')
      } finally {
        this.isSaving = false
      }
    }
  }
})
</script>
