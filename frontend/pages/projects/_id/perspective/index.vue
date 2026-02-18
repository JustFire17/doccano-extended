<template>
  <div>
    <v-card>
      <v-card-title>
        <v-btn
          class="text-capitalize ms-2"
          color="primary"
          @click="$router.push('perspective/add')"
        >
          {{ $t('generic.create') }}
        </v-btn>

        <v-btn 
          class="text-capitalize ms-2" 
          color="primary" 
          @click="openAssociationDialog"
        >
          {{ hasAssociatedPerspective ? 'Dissociate Perspective' : 'Associate Perspective' }}
        </v-btn>

        <v-btn 
          class="text-capitalize ms-2" 
          color="error" 
          @click="openDeleteDialog"
        >
          Delete Perspective
        </v-btn>
      </v-card-title>
      
      <all-perspectives-list
        :items="items"
        :is-loading="isLoading"
        @show-projects="openProjectsModal"
      />
    </v-card>

    <associate-perspective
      v-if="showAssociationDialog"
      :dialog="showAssociationDialog"
      :available-perspectives="perspectives"
      :current-perspective="associatedPerspective"
      @update:dialog="showAssociationDialog = $event"
      @associate="handleAssociate"
      @dissociate="handleDissociate"
    />

    <delete-perspective
      v-if="showDeleteDialog"
      :dialog="showDeleteDialog"
      :available-perspectives="perspectives"
      @update:dialog="showDeleteDialog = $event"
      @delete="handleDelete"
    />

    <v-dialog v-model="showProjectsModal" max-width="500px">
      <v-card>
        <v-card-title class="headline">Associated Projects</v-card-title>
        <v-card-text>
          <div v-if="!selectedPerspective || !selectedPerspective.associated_projects || selectedPerspective.associated_projects.length === 0" style="color: #bdbdbd;">
            No associated projects
          </div>
          <v-list v-else>
            <v-list-item v-for="project in selectedPerspective.associated_projects" :key="project.id">
              <v-list-item-content>
                <v-list-item-title>{{ project.name }} (v{{ project.version }})</v-list-item-title>
              </v-list-item-content>
            </v-list-item>
          </v-list>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn color="primary" text @click="showProjectsModal = false">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script lang="ts">
import Vue from 'vue'
import AllPerspectivesList from '@/components/perspective/AllPerspectivesList.vue'
import AssociatePerspective from '@/components/perspective/AssociatePerspective.vue'
import DeletePerspective from '@/components/perspective/DeletePerspective.vue'

export default Vue.extend({  
  components: {
    AllPerspectivesList,
    AssociatePerspective,
    DeletePerspective
  },

  layout: 'project',

  middleware: ['check-auth', 'auth', 'setCurrentProject'],

  data() {
    return {
      items: [] as any[],
      perspectives: [] as any[],
      currentPerspective: null as any,
      isLoading: false,
      showAssociationDialog: false,
      showDeleteDialog: false,
      showProjectsModal: false,
      selectedPerspective: null as any,
      error: null as string | null
    }
  },

  computed: {
    associatedPerspective(): any {
      if (!this.currentPerspective) return null
      return this.perspectives.find(p => p.id === this.currentPerspective) || null
    },
    projectId(): string {
      return this.$route.params.id
    },
    servicePerspective(): any {
      return this.$services.perspective
    },
    serviceProject(): any {
      return this.$services.project
    },
    hasAssociatedPerspective(): boolean {
      return this.currentPerspective !== null && this.currentPerspective !== undefined
    },
    hasPerspectives(): boolean {
      return this.perspectives && this.perspectives.length > 0
    }
  },

  async created() {
    await this.loadData()
  },

  methods: {
    async loadData() {
      this.isLoading = true
      this.error = null
      try {
        const [perspectives, currentProject] = await Promise.all([
          this.servicePerspective.listAll(this.projectId),
          this.serviceProject.findById(this.projectId)
        ])
        this.items = perspectives
        this.perspectives = perspectives
        this.currentPerspective = currentProject.perspective_associated
      } catch (error: any) {
        console.error('Error loading data:', error)
        this.error = error.response?.data?.detail || "Sorry, we couldn't load the perspectives right now. Please try again in a few moments."
        alert(this.error)
      } finally {
        this.isLoading = false
      }
    },

    openAssociationDialog() {
      if (!this.hasPerspectives) {
        alert('No perspectives available to associate. Please create a perspective first.')
        return
      }
      this.showAssociationDialog = true
    },

    async handleAssociate(perspectiveId: number) {
      try {
        await this.servicePerspective.associatePerspective(this.projectId, perspectiveId)
        await this.loadData()
        alert('Perspective associated with success!')
      } catch (error: any) {
        console.error('Error associating perspective:', error)
        alert(error.response?.data?.error || 'Error associating perspective. Please try again.')
      }
    },

    async handleDissociate() {
      try {
        await this.servicePerspective.removeAssociation(this.projectId)
        await this.loadData()
        alert('Perspective successfully disassociated!')
      } catch (error: any) {
        console.error('Error when dissociating perspective:', error)
        alert(error.response?.data?.error || 'Error when dissociating perspective. Please try again.')
      }
    },

    openDeleteDialog() {
      if (!this.hasPerspectives) {
        alert('No perspectives available to delete.')
        return
      }
      this.showDeleteDialog = true
    },

    async handleDelete(perspectiveId: number) {
      try {
        await this.servicePerspective.deletePerspectiveTotal(this.projectId, perspectiveId)
        await this.loadData()
        alert('Perspective deleted successfully!')
      } catch (error: any) {
        console.error('Error deleting perspective:', error)
        if (error.response?.status === 500) {
          alert('Database unavailable. Please try again later')
        } else if (error.response?.data?.error) {
          alert(error.response.data.error)
        } else {
          alert('Error deleting perspective. Please try again.')
        }
      }
    },

    openProjectsModal(perspective: any) {
      this.selectedPerspective = perspective
      this.showProjectsModal = true
    }
  }
})
</script>