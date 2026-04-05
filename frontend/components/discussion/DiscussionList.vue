<template>
  <v-card>
    <v-card-title>
      <span class="text-h6">Discussions</span>
      <v-spacer />
      <v-btn
        v-if="isProjectAdmin"
        color="primary"
        @click="handleCreateDiscussion"
      >
        CREATE DISCUSSION
      </v-btn>
    </v-card-title>
    
    <v-card-text>
      <!-- Filters -->
      <v-toolbar flat>
        <v-text-field
          v-model="search"
          append-icon="mdi-magnify"
          label="Search"
          single-line
          hide-details
          class="mx-2"
          style="max-width: 300px"
          @input="fetchDiscussions"
        />
        <v-select
          v-model="statusFilter"
          :items="statusOptions"
          label="Status"
          single-line
          hide-details
          class="mx-2"
          style="max-width: 200px"
          @change="fetchDiscussions"
        />
        <v-select
          v-model="versionFilter"
          :items="versionOptions"
          label="Version"
          single-line
          hide-details
          class="mx-2"
          style="max-width: 200px"
          @change="applyVersionFilter"
        />
      </v-toolbar>

      <!-- Version Filter Info -->
      <div v-if="versionFilter !== 'all'" class="mb-4">
        <v-alert
          color="info"
          outlined
          dense
          class="mb-3"
        >
          <v-icon left>mdi-filter</v-icon>
          Showing discussions for {{ versionFilter === currentProject?.version ? 'current version' : 'version' }} 
          <strong>v{{ versionFilter }}</strong>
        </v-alert>
      </div>

      <!-- Grouped Discussions -->
      <div v-if="!loading && discussions.length > 0">
        <!-- Current Version Section -->
        <div v-if="currentVersionDiscussions.length > 0">
          <v-divider class="my-4" />
          <div class="d-flex align-center mb-3">
            <v-icon color="green" class="mr-2">mdi-circle</v-icon>
            <h3 class="text-h6 green--text">Versão Atual (v{{ currentProject?.version }})</h3>
          </div>
          
          <v-data-table
            :headers="headers"
            :items="currentVersionDiscussions"
            :options.sync="options"
            :server-items-length="currentVersionDiscussions.length"
            :loading="loading"
            class="elevation-1 mb-6"
            :footer-props="{
              'items-per-page-options': [5, 10, 15, 25, 50, 100]
            }"
          >
            <template #[`item.name`]="{ item }">
              <router-link :to="`/projects/${projectId}/discussions/${item.id}`">
                {{ item.name }}
              </router-link>
            </template>
            
            <template #[`item.status`]="{ item }">
              <v-chip
                :color="getStatusColor(item.status)"
                small
              >
                {{ item.status }}
              </v-chip>
            </template>
            
            <template #[`item.createdAt`]="{ item }">
              <div>
                <div><strong>Created:</strong> {{ formatDate(item.createdAt) }}</div>
                <div v-if="item.updatedAt !== item.createdAt"><strong>Updated:</strong> {{ formatDate(item.updatedAt) }}</div>
              </div>
            </template>
            
            <template #[`item.projectVersion`]="{ item }">
              <v-chip
                small
                color="green"
                text-color="white"
              >
                v{{ item.projectVersion }}
              </v-chip>
            </template>
            
            <template #[`item.annotators`]="{ item }">
              <div v-if="item.annotators && item.annotators.length > 0" class="d-flex flex-wrap">
                <v-chip
                  v-for="annotator in item.annotators"
                  :key="annotator.id"
                  :color="getRoleColor(annotator.role)"
                  text-color="white"
                  small
                  class="ma-1"
                >
                  {{ annotator.username }}
                </v-chip>
              </div>
              <span v-else class="grey--text">No annotators</span>
            </template>
            
            <template #[`item.actions`]="{ item }">
              <template v-if="isProjectAdmin">
                <v-tooltip bottom>
                  <template #activator="{ on, attrs }">
                    <v-btn
                      icon
                      small
                      class="mr-2"
                      v-bind="attrs"
                      v-on="on"
                      @click="openChat(item)"
                    >
                      <v-icon>{{ mdiForumOutline }}</v-icon>
                    </v-btn>
                  </template>
                  <span>Open Discussion</span>
                </v-tooltip>
                
                <v-tooltip bottom>
                  <template #activator="{ on, attrs }">
                    <v-btn 
                      icon 
                      small
                      color="error"
                      v-bind="attrs"
                      :disabled="item.status === 'closed'"
                      v-on="on"
                      @click="deleteDialog = true; selectedDiscussion = item"
                    >
                      <v-icon>{{ mdiDeleteOutline }}</v-icon>
                    </v-btn>
                  </template>
                  <span>{{ item.status === 'closed' ? 'Cannot Delete Closed Discussion' : 'Delete Discussion' }}</span>
                </v-tooltip>
              </template>
            </template>
          </v-data-table>
        </div>

        <!-- Historical Versions Section -->
        <div v-if="historicalVersionDiscussions.length > 0">
          <v-divider class="my-4" />
          <div class="d-flex align-center mb-3">
            <v-icon color="grey" class="mr-2">mdi-history</v-icon>
            <h3 class="text-h6 grey--text">Histórico (Versões Anteriores)</h3>
          </div>
          
          <div v-for="version in historicalVersions" :key="version" class="mb-4">
            <div class="d-flex align-center mb-2">
              <v-icon color="blue-grey" size="16" class="mr-2">mdi-archive</v-icon>
              <h4 class="text-subtitle-1 blue-grey--text">Versão {{ version }}</h4>
            </div>
            
            <v-data-table
              :headers="headers"
              :items="getDiscussionsByVersion(version)"
              :options.sync="options"
              :server-items-length="getDiscussionsByVersion(version).length"
              :loading="loading"
              class="elevation-1 historical-table"
              :footer-props="{
                'items-per-page-options': [5, 10, 15, 25, 50, 100]
              }"
            >
              <template #[`item.name`]="{ item }">
                <router-link :to="`/projects/${projectId}/discussions/${item.id}`" class="grey--text">
                  {{ item.name }}
                </router-link>
              </template>
              
              <template #[`item.status`]="{ item }">
                <v-chip
                  :color="getStatusColor(item.status)"
                  small
                  outlined
                >
                  {{ item.status }}
                </v-chip>
              </template>
              
              <template #[`item.createdAt`]="{ item }">
                <div class="grey--text text--darken-1">
                  <div><strong>Created:</strong> {{ formatDate(item.createdAt) }}</div>
                  <div v-if="item.updatedAt !== item.createdAt"><strong>Updated:</strong> {{ formatDate(item.updatedAt) }}</div>
                </div>
              </template>
              
              <template #[`item.projectVersion`]="{ item }">
                <v-chip
                  small
                  outlined
                  color="blue-grey"
                >
                  v{{ item.projectVersion }}
                </v-chip>
              </template>
              
              <template #[`item.annotators`]="{ item }">
                <div v-if="item.annotators && item.annotators.length > 0" class="d-flex flex-wrap">
                  <v-chip
                    v-for="annotator in item.annotators"
                    :key="annotator.id"
                    :color="getRoleColor(annotator.role)"
                    text-color="dark-grey"
                    small
                    outlined
                    class="ma-1"
                  >
                    {{ annotator.username }}
                  </v-chip>
                </div>
                <span v-else class="grey--text">No annotators</span>
              </template>
              
              <template #[`item.actions`]="{ item }">
                <template v-if="isProjectAdmin">
                  <v-tooltip bottom>
                    <template #activator="{ on, attrs }">
                      <v-btn
                        icon
                        small
                        class="mr-2"
                        v-bind="attrs"
                        v-on="on"
                        @click="openChat(item)"
                      >
                        <v-icon>{{ mdiForumOutline }}</v-icon>
                      </v-btn>
                    </template>
                    <span>Open Discussion</span>
                  </v-tooltip>
                  
                  <v-tooltip bottom>
                    <template #activator="{ on, attrs }">
                      <v-btn 
                        icon 
                        small
                        color="error"
                        v-bind="attrs"
                        disabled
                        v-on="on"
                      >
                        <v-icon>{{ mdiDeleteOutline }}</v-icon>
                      </v-btn>
                    </template>
                    <span>Cannot Delete Previous Version Discussion</span>
                  </v-tooltip>
                </template>
              </template>
            </v-data-table>
          </div>
        </div>
      </div>
      
      <!-- Loading State -->
      <div v-else-if="loading" class="text-center py-4">
        <v-progress-circular indeterminate color="primary" />
        <p class="mt-2">Loading discussions...</p>
      </div>
      
      <!-- Empty State -->
      <div v-else class="text-center py-8">
        <v-icon size="64" color="grey lighten-1">mdi-forum-outline</v-icon>
        <h3 class="text-h6 grey--text mt-2">
          {{ versionFilter !== 'all' ? `No discussions found for v${versionFilter}` : 'No discussions found' }}
        </h3>
        <p class="grey--text">
          {{ versionFilter !== 'all' ? 'Try selecting a different version or create a new discussion' : 'Create your first discussion to get started' }}
        </p>
        <v-btn
          v-if="versionFilter !== 'all'"
          color="primary"
          outlined
          class="mt-3"
          @click="versionFilter = 'all'; applyVersionFilter()"
        >
          Show All Versions
        </v-btn>
      </div>
    </v-card-text>
    
    <!-- Create Discussion Dialog -->
    <v-dialog v-model="createDialog" max-width="500px">
      <v-card>
        <v-card-title>
          <span class="headline">Create Discussion</span>
        </v-card-title>
        <v-card-text>
          <v-container>
            <v-row>
              <v-col cols="12">
                <v-text-field
                  v-model="newDiscussion.name"
                  label="Discussion Name"
                  required
                />
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn color="blue darken-1" text @click="createDialog = false">
            Cancel
          </v-btn>
          <v-btn color="blue darken-1" text @click="createDiscussion">
            Create
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- Delete Discussion Dialog -->
    <v-dialog v-model="deleteDialog" max-width="500px">
      <v-card>
        <v-card-title>
          <span class="headline">Delete Discussion</span>
        </v-card-title>
        <v-card-text>
          Are you sure you want to delete this discussion?
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn color="blue darken-1" text @click="deleteDialog = false">
            Cancel
          </v-btn>
          <v-btn color="red darken-1" text @click="deleteDiscussion">
            Delete
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script>
import {
  mdiForumOutline,
  mdiDeleteOutline
} from '@mdi/js'
import { mapGetters } from 'vuex'
import { Discussion } from '~/domain/models/discussion/discussion'

export default {
  props: {
    projectId: {
      type: String,
      required: true
    }
  },
  
  data() {
    return {
      discussions: [],
      loading: false,
      totalDiscussions: 0,
      search: '',
      options: {
        page: 1,
        itemsPerPage: 10,
        sortBy: ['updatedAt'],
        sortDesc: [true]
      },
      statusFilter: 'all',
      statusOptions: [
        { text: 'All', value: 'all' },
        { text: 'Open', value: 'open' },
        { text: 'Closed', value: 'closed' }
      ],
      versionFilter: 'all',
      allDiscussions: [], // Store all discussions before filtering
      createDialog: false,
      deleteDialog: false,
      selectedDiscussion: null,
      newDiscussion: {
        name: ''
      },
      // MDI icons
      mdiForumOutline,
      mdiDeleteOutline,
      isProjectAdmin: false
    }
  },
  
  computed: {
    currentUser() {
      return this.$store.getters['auth/getUser']
    },
    
    ...mapGetters('projects', ['currentProject']),
    
    headers() {
      const baseHeaders = [
        { text: 'Name', value: 'name' },
        { text: 'Created By', value: 'createdByUsername' },
        { text: 'Status', value: 'status' },
        { text: 'Created At', value: 'createdAt' },
        { text: 'Project Version', value: 'projectVersion' },
        { text: 'Annotators', value: 'annotators' }
      ]
      
      // Adicionar coluna de ações apenas para administradores
      if (this.isProjectAdmin) {
        baseHeaders.push({ text: 'Actions', value: 'actions', sortable: false })
      }
      
      return baseHeaders
    },
    
    versionOptions() {
      // Get all unique versions from all discussions and create options
      const allVersions = [...new Set(this.allDiscussions.map(d => d.projectVersion))].sort((a, b) => b - a)
      const options = [{ text: 'All Versions', value: 'all' }]
      
      // Add current version option
      if (this.currentProject?.version) {
        options.push({ text: `Current (v${this.currentProject.version})`, value: this.currentProject.version })
      }
      
      // Add historical versions
      const historicalVersions = allVersions.filter(v => v !== this.currentProject?.version)
      historicalVersions.forEach(version => {
        options.push({ text: `v${version}`, value: version })
      })
      
      return options
    },
    
    filteredDiscussions() {
      if (this.versionFilter === 'all') {
        return this.discussions
      }
      return this.discussions.filter(d => d.projectVersion === this.versionFilter)
    },
    
    currentVersionDiscussions() {
      return this.filteredDiscussions.filter(d => d.projectVersion === this.currentProject?.version)
    },
    
    historicalVersionDiscussions() {
      return this.filteredDiscussions.filter(d => d.projectVersion !== this.currentProject?.version)
    },
    
    historicalVersions() {
      return [...new Set(this.historicalVersionDiscussions.map(d => d.projectVersion))].sort((a, b) => b - a)
    }
  },
  
  async created() {
    // Ensure auth is initialized
    await this.$store.dispatch('auth/initAuth')
    // Fetch user role
    const member = await this.$repositories.member.fetchMyRole(this.projectId)
    this.isProjectAdmin = member.isProjectAdmin
    
    // Make sure current project is set
    await this.$store.dispatch('projects/setCurrentProject', this.projectId)
    
    this.fetchDiscussions()
  },
  
  methods: {
    async fetchDiscussions() {
      this.loading = true
      
      try {
        const { page, itemsPerPage, sortBy, sortDesc } = this.options
        const status = this.statusFilter !== 'all' ? this.statusFilter : ''
        const offset = (page - 1) * itemsPerPage
        
        const mainSortBy = sortBy.length > 0 ? sortBy[0] : 'updatedAt'
        const mainSortDesc = sortDesc.length > 0 ? sortDesc[0] : true
        
        const query = new this.$services.discussion.SearchQuery(
          itemsPerPage.toString(),
          offset.toString(),
          status,
          mainSortBy,
          mainSortDesc.toString()
        )
        
        const response = await this.$services.discussion.listDiscussions(this.projectId, query)
        this.allDiscussions = response.items // Store all discussions for version filtering
        this.discussions = response.items
        this.totalDiscussions = response.count
      } catch (error) {
        console.error('Error fetching discussions:', error);
        // Check for any indication of a 500 error
        if (error?.response?.status === 500 || 
            error?.message?.includes('500') || 
            error?.toString().includes('500')) {
          alert('Database unavailable. Please try again later');
        }
        this.discussions = [];
        this.allDiscussions = [];
        this.totalDiscussions = 0;
      } finally {
        this.loading = false;
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString()
    },
    
    getStatusColor(status) {
      return status === 'open' ? 'green' : 'error'
    },
    
    getRoleColor(role) {
      switch (role) {
        case 'annotator':
          return 'blue'
        case 'annotation_approver':
          return 'green'
        case 'project_admin':
          return 'purple'
        default:
          return 'grey'
      }
    },
    
    openCreateDialog() {
      this.newDiscussion = { name: '' }
      this.createDialog = true
    },
    
    openChat(discussion) {
      this.$router.push(`/projects/${this.projectId}/discussions/${discussion.id}`)
    },
    
    handleCreateDiscussion() {
      // Check if project is closed
      if (!this.currentProject || !this.currentProject.closed) {
        alert('Project must be closed to create a discussion.')
        this.$router.push(`/projects/${this.projectId}/dataset`)
        return
      }
      
      // Check if a discussion already exists for this project version
      const currentVersion = this.currentProject.version
      const existingDiscussionForVersion = this.discussions.find(
        discussion => discussion.projectVersion === currentVersion
      )
      
      if (existingDiscussionForVersion) {
        alert(`Cannot create a new discussion. A discussion already exists for project version ${currentVersion}.`)
        return
      }
      
      // If project is closed and no discussion exists for this version, open the create dialog
      this.openCreateDialog()
    },
    
    async createDiscussion() {
      if (!this.newDiscussion.name.trim()) {
        alert('Discussion name is required')
        return
      }
      
      try {
        console.log('Current user:', this.currentUser)
        const currentUserId = this.currentUser ? this.currentUser.id : null
        
        if (!currentUserId) {
          alert(`You must be logged in to create a discussion. Auth state: ${this.$store.state.auth.isAuthenticated}, Username: ${this.$store.state.auth.username}`)
          return
        }
        
        const discussion = new Discussion(
          0,
          this.projectId,
          this.newDiscussion.name,
          currentUserId,
          '',
          'open',
          '',
          '',
          [],
          0
        )
        
        await this.$services.discussion.createDiscussion(this.projectId, discussion)
        this.createDialog = false
        this.fetchDiscussions()
        alert('Discussion created successfully')
      } catch (error) {
        console.error('Error creating discussion:', error);
        // Check for any indication of a 500 error
        if (error?.response?.status === 500 || 
            error?.message?.includes('500') || 
            error?.toString().includes('500')) {
          alert('Database unavailable. Please try again later');
        }
        this.createDialog = false;
      }
    },
    
    async deleteDiscussion() {
      try {
        if (!this.selectedDiscussion) return
        
        // Check if the discussion is closed
        if (this.selectedDiscussion.status === 'closed') {
          alert('Cannot delete a closed discussion')
          this.deleteDialog = false
          return
        }
        
        await this.$services.discussion.deleteDiscussion(this.projectId, this.selectedDiscussion.id)
        this.deleteDialog = false
        this.fetchDiscussions()
        alert('Discussion deleted successfully')
      } catch (error) {
        console.error('Error deleting discussion:', error);
        // Check for any indication of a 500 error
        if (error?.response?.status === 500 || 
            error?.message?.includes('500') || 
            error?.toString().includes('500')) {
          alert('Database unavailable. Please try again later');
        }
        this.deleteDialog = false;
      }
    },
    
    getDiscussionsByVersion(version) {
      return this.filteredDiscussions.filter(d => d.projectVersion === version)
    },
    
    applyVersionFilter() {
      // Apply version filter by updating the discussions array
      if (this.versionFilter === 'all') {
        this.discussions = [...this.allDiscussions]
      } else {
        this.discussions = this.allDiscussions.filter(d => d.projectVersion === this.versionFilter)
      }
    }
  }
}
</script>

<style scoped>
.historical-table {
  opacity: 0.8;
}

.historical-table >>> .v-data-table__wrapper {
  background-color: #fafafa;
}

.historical-table >>> .v-data-table tbody tr {
  background-color: #f5f5f5;
}

.historical-table >>> .v-data-table tbody tr:hover {
  background-color: #eeeeee !important;
}

.historical-table >>> .v-chip {
  opacity: 0.9;
}

.v-divider {
  border-color: #e0e0e0 !important;
}

.green--text {
  color: #4caf50 !important;
}

.blue-grey--text {
  color: #607d8b !important;
}
</style> 