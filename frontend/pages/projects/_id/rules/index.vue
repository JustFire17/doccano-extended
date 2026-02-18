<template>
  <v-container>
    <v-row>
      <v-col>
        <v-card>
          <v-card-title>
            <v-row align="center">
              <v-col>
                <h1 class="text-h4">{{ $t('projectRules.title') }}</h1>
              </v-col>
              <v-col class="text-right">
                <v-btn
                  v-if="isProjectAdmin && project.closed"
                  color="error"
                  class="mr-2"
                  :disabled="selected.length === 0"
                  @click="deleteDialog = true"
                >
                  Delete Selected
                </v-btn>
                <v-btn
                  v-if="isProjectAdmin && project.closed"
                  color="primary"
                  @click="createDialog = true"
                >
                  Create Rule
                </v-btn>
                <v-btn
                  v-else-if="isProjectAdmin"
                  color="primary"
                  disabled
                  title="The project must be closed to create new rules"
                >
                  Create Rule
                </v-btn>
              </v-col>
            </v-row>
          </v-card-title>
          <v-card-text>
            <v-data-table
              v-model="selected"
              :headers="headers"
              :items="rules"
              :loading="isLoading"
              show-select
              class="elevation-1"
              :item-class="getItemClass"
            >
              <template #[`item.description`]="{ item }">
                <div>
                  {{ item.description }}
                </div>
              </template>
              <template #[`item.createdAt`]="{ item }">
                <div>
                  {{ formatDate(item.createdAt) }}
                </div>
              </template>
              <template #[`item.votingEnd`]="{ item }">
                <div>
                  {{ item.votingEndDate ? formatDate(item.votingEndDate + ' ' + (item.votingEndTime || '23:59')) : '-' }}
                </div>
              </template>
              <template #[`item.votePercentage`]="{ item }">
                <div v-if="!isProjectAdmin && !isVotingEnded(item) && !item.votingClosed">
                  <span class="white--text">Voting In Progress</span>
                </div>
                <div v-else-if="item.upvotesCount + item.downvotesCount === 0">
                  <span class="white--text">No Votes Recorded</span>
                </div>
                <v-progress-linear
                  :value="item.votePercentage"
                  :color="getVoteColor(item.votePercentage)"
                  height="20"
                >
                  <span class="white--text">{{ item.votePercentage }}%</span>
                </v-progress-linear>
              </template>
              <template #[`item.vote`]="{ item }">
                <div v-if="isProjectAdmin">
                  <v-btn
                    v-if="!item.votingClosed && item.version === project.version"
                    class="mr-2"
                    small
                    color="error"
                    @click="confirmCloseVote(item)"
                  >
                    Close Vote
                  </v-btn>
                  <v-btn
                    v-else-if="item.votingClosed && item.version === project.version"
                    small
                    color="success"
                    @click="confirmReopenVote(item)"
                  >
                    Reopen Vote
                  </v-btn>
                  <span v-else class="text-caption grey--text">
                    Can't edit previous version
                  </span>
                </div>
                <div v-else>
                  <v-btn
                    v-if="!isVotingEnded(item) && item.version === project.version"
                    class="mr-2"
                    small
                    :color="getUserVote(item) === 'upvote' ? 'success' : 'grey'"
                    @click="upvoteRule(item)"
                  >
                    <v-icon>{{ mdiCheck }}</v-icon>
                  </v-btn>
                  <v-btn
                    v-if="!isVotingEnded(item) && item.version === project.version"
                    small
                    :color="getUserVote(item) === 'downvote' ? 'error' : 'grey'"
                    @click="downvoteRule(item)"
                  >
                    <v-icon>{{ mdiClose }}</v-icon>
                  </v-btn>
                  <v-icon v-else-if="isVotingEnded(item)">{{ mdiLock }}</v-icon>
                  <span v-else class="text-caption grey--text">
                    Can't vote on previous version
                  </span>
                </div>
              </template>
            </v-data-table>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Create Rule Dialog -->
    <v-dialog v-model="createDialog" max-width="500px">
      <v-card>
        <v-card-title>Create Rule</v-card-title>
        <v-card-text>
          <v-form ref="form" v-model="valid">
            <v-text-field
              v-model="newRule.name"
              label="Rule Name"
              required
            ></v-text-field>
            <v-textarea
              v-model="newRule.description"
              label="Description"
              required
            ></v-textarea>
            <v-menu
              ref="dateMenu"
              v-model="dateMenu"
              :close-on-content-click="false"
              transition="scale-transition"
              offset-y
              min-width="auto"
            >
              <template #activator="{ on, attrs }">
                <v-text-field
                  v-model="newRule.votingEndDate"
                  label="Voting End Date"
                  prepend-icon="mdi-calendar"
                  readonly
                  v-bind="attrs"
                  v-on="on"
                ></v-text-field>
              </template>
              <v-date-picker
                v-model="newRule.votingEndDate"
                :min="minDate"
                @input="dateMenu = false"
              ></v-date-picker>
            </v-menu>
            <v-menu
              ref="timeMenu"
              v-model="timeMenu"
              :close-on-content-click="false"
              transition="scale-transition"
              offset-y
              min-width="auto"
            >
              <template #activator="{ on, attrs }">
                <v-text-field
                  v-model="newRule.votingEndTime"
                  label="Voting End Time"
                  prepend-icon="mdi-clock"
                  readonly
                  v-bind="attrs"
                  v-on="on"
                ></v-text-field>
              </template>
              <v-time-picker
                v-model="newRule.votingEndTime"
                :min="minTime"
                format="24hr"
                @change="timeMenu = false"
              ></v-time-picker>
            </v-menu>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="error" text @click="createDialog = false">
            Cancel
          </v-btn>
          <v-btn color="primary" @click="createRule">
            Create
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Vote Dialog -->
    <v-dialog v-model="voteDialog" max-width="400px">
      <v-card>
        <v-card-title>Confirm Vote</v-card-title>
        <v-card-text>
          Are you sure you want to submit your vote?
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="error" text @click="voteDialog = false">
            Cancel
          </v-btn>
          <v-btn color="primary" @click="confirmVote">
            Confirm
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Close Vote Dialog -->
    <v-dialog v-model="closeVoteDialog" max-width="400px">
      <v-card>
        <v-card-title>Close Vote</v-card-title>
        <v-card-text>
          Are you sure you want to close this vote?
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="error" text @click="closeVoteDialog = false">
            Cancel
          </v-btn>
          <v-btn color="primary" @click="executeCloseVote">
            Confirm
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Reopen Vote Dialog -->
    <v-dialog v-model="reopenVoteDialog" max-width="500px">
      <v-card>
        <v-card-title>Reopen Vote</v-card-title>
        <v-card-text>
          <v-form ref="reopenForm" v-model="valid">
            <v-menu
              ref="reopenDateMenu"
              v-model="reopenDateMenu"
              :close-on-content-click="false"
              transition="scale-transition"
              offset-y
              min-width="auto"
            >
              <template #activator="{ on, attrs }">
                <v-text-field
                  v-model="newVotingEndDate"
                  label="Voting End Date"
                  prepend-icon="mdi-calendar"
                  readonly
                  v-bind="attrs"
                  v-on="on"
                ></v-text-field>
              </template>
              <v-date-picker
                v-model="newVotingEndDate"
                :min="minDate"
                @input="reopenDateMenu = false"
              ></v-date-picker>
            </v-menu>
            <v-menu
              ref="reopenTimeMenu"
              v-model="reopenTimeMenu"
              :close-on-content-click="false"
              transition="scale-transition"
              offset-y
              min-width="auto"
            >
              <template #activator="{ on, attrs }">
                <v-text-field
                  v-model="newVotingEndTime"
                  label="Voting End Time"
                  prepend-icon="mdi-clock"
                  readonly
                  v-bind="attrs"
                  v-on="on"
                ></v-text-field>
              </template>
              <v-time-picker
                v-model="newVotingEndTime"
                :min="minTime"
                format="24hr"
                @change="reopenTimeMenu = false"
              ></v-time-picker>
            </v-menu>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="error" text @click="reopenVoteDialog = false">
            Cancel
          </v-btn>
          <v-btn color="primary" @click="executeReopenVote">
            Confirm
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete Dialog -->
    <v-dialog v-model="deleteDialog" max-width="400px">
      <v-card>
        <v-card-title>Confirm Deletion</v-card-title>
        <v-card-text>
          Are you sure you want to delete {{ selected.length }} selected rule(s)?
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="error" text @click="deleteDialog = false">
            Cancel
          </v-btn>
          <v-btn color="primary" @click="deleteRules">
            Confirm
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Error Snackbar -->
    <v-snackbar v-model="showError" color="error">
      {{ errorMessage }}
      <template #action="{ attrs }">
        <v-btn text v-bind="attrs" @click="showError = false">
          Close
        </v-btn>
      </template>
    </v-snackbar>
  </v-container>
</template>

<script lang="ts">
import Vue from 'vue'
import { dateFormat } from '@vuejs-community/vue-filter-date-format'
import { dateParse } from '@vuejs-community/vue-filter-date-parse'
import { mdiCheck, mdiClose, mdiLock } from '@mdi/js'
import { Context } from '@nuxt/types'
import { Rule } from '@/domain/models/rule/rule'

interface ComponentData {
  isLoading: boolean
  rules: Rule[]
  selected: Rule[]
  createDialog: boolean
  deleteDialog: boolean
  voteDialog: boolean
  closeVoteDialog: boolean
  reopenVoteDialog: boolean
  dateMenu: boolean
  timeMenu: boolean
  voteType: 'upvote' | 'downvote' | null
  ruleToVote: Rule | null
  ruleToCloseVote: Rule | null
  ruleToReopenVote: Rule | null
  newRule: {
    name: string
    description: string
    votingEndDate: string
    votingEndTime: string
  }
  baseHeaders: Array<{ text: string; value: string }>
  isProjectAdmin: boolean
  errorMessage: string
  showError: boolean
  mdiCheck: string
  mdiClose: string
  mdiLock: string
  project: any
  valid: boolean
  newVotingEndDate: string
  reopenDateMenu: boolean
  reopenTimeMenu: boolean
  newVotingEndTime: string
  checkInterval: NodeJS.Timeout | null
}

interface ComponentMethods {
  loadRules(): Promise<void>
  createRule(): Promise<void>
  deleteRules(): Promise<void>
  getUserVote(rule: Rule): 'upvote' | 'downvote' | null
  isVotingEnded(rule: Rule): boolean
  upvoteRule(rule: Rule): Promise<void>
  downvoteRule(rule: Rule): Promise<void>
  confirmVote(): Promise<void>
  voteRule(rule: Rule, isUpvote: boolean): Promise<void>
  confirmCloseVote(rule: Rule): void
  executeCloseVote(): Promise<void>
  closeRuleVote(rule: Rule): Promise<void>
  confirmReopenVote(rule: Rule): void
  executeReopenVote(): Promise<void>
  reopenRuleVote(rule: Rule): Promise<void>
  getVoteColor(percentage: number): string
  formatDate(date: string | Date): string
  getItemClass(item: Rule): string
  checkVotingStatus(): Promise<void>
}

interface ComponentComputed {
  headers: any[]
  minDate: string
  minTime: string
}

export default Vue.extend<ComponentData, ComponentMethods, ComponentComputed>({
  layout: 'project',
  middleware: ['check-auth', 'auth', 'setCurrentProject'],
  validate(context: Context) {
    return /^\d+$/.test(context.params.id)
  },
  data(): ComponentData {
    return {
      isLoading: false,
      rules: [],
      selected: [],
      createDialog: false,
      deleteDialog: false,
      voteDialog: false,
      closeVoteDialog: false,
      reopenVoteDialog: false,
      dateMenu: false,
      timeMenu: false,
      voteType: 'upvote',
      ruleToVote: null,
      ruleToCloseVote: null,
      ruleToReopenVote: null,
      newRule: {
        name: '',
        description: '',
        votingEndDate: '',
        votingEndTime: ''
      },
      baseHeaders: [
        { text: 'Name', value: 'name' },
        { text: 'Description', value: 'description' },
        { text: 'Version', value: 'version' },
        { text: 'Created At', value: 'createdAt' },
        { text: 'Voting Ends', value: 'votingEnd' }
      ],
      isProjectAdmin: false,
      errorMessage: '',
      showError: false,
      mdiCheck,
      mdiClose,
      mdiLock,
      project: {},
      valid: true,
      newVotingEndDate: '',
      reopenDateMenu: false,
      reopenTimeMenu: false,
      newVotingEndTime: '',
      checkInterval: null
    }
  },
  computed: {
    headers(): any[] {
      const voteHeaders = this.isProjectAdmin 
        ? [
            { text: 'Status', value: 'votePercentage', align: 'center', width: '300px' },
            { text: 'Actions', value: 'vote', align: 'center', sortable: false, width: '180px' }
          ]
        : [
            { text: 'Status & Results', value: 'votePercentage', align: 'center', width: '250px' },
            { text: 'Your Vote', value: 'vote', align: 'center', sortable: false, width: '150px' }
          ];
      
      return [...this.baseHeaders.slice(0, 2), ...voteHeaders, ...this.baseHeaders.slice(2)];
    },
    minDate(): string {
      return new Date().toISOString().substr(0, 10)
    },
    minTime(): string {
      const now = new Date()
      const hours = now.getHours().toString().padStart(2, '0')
      const minutes = now.getMinutes().toString().padStart(2, '0')
      const currentTime = `${hours}:${minutes}`
      return this.newRule.votingEndDate === this.minDate ? currentTime : '00:00'
    }
  },
  async created() {
    try {
      // Debug translations
      console.log('Available translations:', {
        projectRules: this.$t('projectRules'),
        common: this.$t('common')
      })

      // Check if project version is > 1
      const project = await this.$repositories.project.findById(this.$route.params.id)
      if (project.version <= 1 && !project.closed) {
        return this.$router.push(this.localePath('/projects/' + this.$route.params.id))
      }

      // Load rules and check if user is admin
      await this.loadRules()
      const member = await this.$repositories.member.fetchMyRole(this.$route.params.id)
      this.isProjectAdmin = member.isProjectAdmin
      this.project = project

      // Iniciar verificação periódica do estado das votações
      this.checkInterval = setInterval(() => {
        this.checkVotingStatus()
      }, 60000) // Verificar a cada minuto
    } catch (e) {
      this.errorMessage = 'Failed to load rules page'
      this.showError = true
      console.error('Error in created:', e)
    }
  },
  beforeDestroy() {
    // Limpar o intervalo quando o componente for destruído
    if (this.checkInterval) {
      clearInterval(this.checkInterval)
    }
  },
  methods: {
    async loadRules() {
      this.isLoading = true
      try {
        this.rules = await this.$services.project.listRules(this.$route.params.id)
        // Log para depuração
        console.log('Rules loaded:', this.rules.map(rule => ({
          id: rule.id,
          name: rule.name,
          votingClosed: rule.votingClosed
        })))
      } catch (error) {
        this.errorMessage = 'Error loading rules'
        this.showError = true
      } finally {
        this.isLoading = false
      }
    },
    async createRule() {
      try {
        if (!this.project.closed) {
          this.errorMessage = this.$t('projectRules.projectMustBeClosed')
          this.showError = true
          return
        }
        await this.$services.project.createRule(
          this.$route.params.id,
          this.newRule.name,
          this.newRule.description,
          this.project.version,
          this.newRule.votingEndDate,
          this.newRule.votingEndTime
        )
        this.createDialog = false
        this.loadRules()
      } catch (error: any) {
        if (error.response?.status === 500) {
          this.errorMessage = 'Database unavailable. Please try again later'
        } else {
          this.errorMessage = error.response?.data?.detail || error.message
        }
        this.showError = true
      }
    },
    async deleteRules() {
      try {
        if (!this.project.closed) {
          this.errorMessage = this.$t('projectRules.projectMustBeClosed')
          this.showError = true
          return
        }

        // Filter out rules from previous versions
        const rulesToDelete = this.selected.filter(rule => rule.version === this.project.version)
        
        if (rulesToDelete.length === 0) {
          this.errorMessage = 'Cannot delete rules from previous project versions'
          this.showError = true
          this.deleteDialog = false
          return
        }

        for (const rule of rulesToDelete) {
          await this.$services.project.deleteRule(this.$route.params.id, rule.id)
        }
        this.rules = this.rules.filter(rule => !rulesToDelete.includes(rule))
        this.selected = []
        this.deleteDialog = false
      } catch (error: any) {
        if (error.response?.status === 500) {
          this.errorMessage = 'Database unavailable. Please try again later.'
        } else {
          this.errorMessage = 'Error deleting rules'
        }
        this.showError = true
      }
    },
    getUserVote(rule: Rule): 'upvote' | 'downvote' | null {
      return rule.userVote || null
    },
    isVotingEnded(rule: Rule): boolean {
      if (!rule.votingEndDate) return false
      
      const now = new Date()
      const endDate = new Date(rule.votingEndDate)
      
      if (rule.votingEndTime) {
        const [hours, minutes] = rule.votingEndTime.split(':')
        endDate.setHours(parseInt(hours), parseInt(minutes))
      } else {
        endDate.setHours(23, 59, 59)
      }
      
      // Se o tempo expirou, atualiza o estado da votação no backend
      if (now > endDate && !rule.votingClosed) {
        this.closeRuleVote(rule)
      }
      
      return now > endDate || rule.votingClosed
    },
    async upvoteRule(rule: Rule) {
      if (this.isVotingEnded(rule)) {
        this.errorMessage = 'Voting has ended for this rule'
        this.showError = true
        return
      }
      
      const currentVote = this.getUserVote(rule)
      if (currentVote === 'upvote') {
        // Se já votou positivamente, remove o voto
        await this.voteRule(rule, true)
      } else {
        this.voteType = 'upvote'
        this.ruleToVote = rule
        this.voteDialog = true
      }
    },
    async downvoteRule(rule: Rule) {
      if (this.isVotingEnded(rule)) {
        this.errorMessage = 'Voting has ended for this rule'
        this.showError = true
        return
      }
      
      const currentVote = this.getUserVote(rule)
      if (currentVote === 'downvote') {
        // Se já votou negativamente, remove o voto
        await this.voteRule(rule, false)
      } else {
        this.voteType = 'downvote'
        this.ruleToVote = rule
        this.voteDialog = true
      }
    },
    async confirmVote() {
      if (this.ruleToVote) {
        await this.voteRule(this.ruleToVote, this.voteType === 'upvote')
        this.voteDialog = false
        this.ruleToVote = null
      }
    },
    async voteRule(rule: Rule, isUpvote: boolean) {
      try {
        if (rule.version !== this.project.version) {
          this.errorMessage = 'Cannot vote on rules from previous project versions'
          this.showError = true
          return
        }

        if (this.isVotingEnded(rule)) {
          this.errorMessage = 'Voting period for this rule has ended'
          this.showError = true
          return
        }

        const projectId = parseInt(this.$route.params.id, 10)
        await this.$services.project.voteRule(projectId, rule.id, isUpvote)
        await this.loadRules()
      } catch (error: any) {
        console.error('Error voting on rule:', error)
        if (error.response?.status === 500) {
          this.errorMessage = error.response.data?.detail || 'Database unavailable. Please try again later.'
        } else if (error.response?.data?.detail) {
          this.errorMessage = error.response.data.detail
        } else {
          this.errorMessage = 'Error voting on rule'
        }
        this.showError = true
      }
    },
    getVoteColor(percentage: number): string {
      if (percentage >= 75) return 'success'
      if (percentage >= 50) return 'warning'
      return 'error'
    },
    formatDate(date: string | Date): string {
      if (!date) return '-'
      try {
        const parsedDate = typeof date === 'string' ? dateParse(date) : date
        return dateFormat(parsedDate, 'DD/MM/YYYY HH:mm')
      } catch (error) {
        console.error('Error formatting date:', error)
        return '-'
      }
    },
    confirmCloseVote(rule: Rule) {
      this.ruleToCloseVote = rule
      this.closeVoteDialog = true
    },
    async executeCloseVote() {
      if (this.ruleToCloseVote) {
        await this.closeRuleVote(this.ruleToCloseVote)
        this.closeVoteDialog = false
        this.ruleToCloseVote = null
      }
    },
    async closeRuleVote(rule: Rule) {
      try {
        const projectId = parseInt(this.$route.params.id, 10)
        const updatedRule = await this.$services.project.closeRuleVote(projectId, rule.id)
        console.log('Regra após fechar votação:', updatedRule)
        await this.loadRules()
      } catch (error: any) {
        console.error('Error closing rule vote:', error)
        if (error.response?.status === 500) {
          this.errorMessage = error.response.data?.detail || 'Database unavailable. Please try again later.'
        } else if (error.response?.data?.detail) {
          this.errorMessage = error.response.data.detail
        } else {
          this.errorMessage = 'Error closing rule vote'
        }
        this.showError = true
      }
    },
    confirmReopenVote(rule: Rule) {
      this.ruleToReopenVote = rule
      this.newVotingEndDate = ''
      this.newVotingEndTime = ''
      this.reopenVoteDialog = true
    },
    async executeReopenVote() {
      if (this.ruleToReopenVote) {
        if (!this.newVotingEndDate) {
          this.errorMessage = 'Please select an end date for the voting'
          this.showError = true
          return
        }
        await this.reopenRuleVote(this.ruleToReopenVote)
        this.reopenVoteDialog = false
        this.ruleToReopenVote = null
      }
    },
    async reopenRuleVote(rule: Rule) {
      try {
        const projectId = parseInt(this.$route.params.id, 10)
        const updatedRule = await this.$services.project.reopenRuleVote(
          projectId, 
          rule.id,
          this.newVotingEndDate,
          this.newVotingEndTime
        )
        console.log('Regra após reabrir votação:', updatedRule)
        await this.loadRules()
      } catch (error: any) {
        console.error('Error reopening rule vote:', error)
        if (error.response?.status === 500) {
          this.errorMessage = error.response.data?.detail || 'Database unavailable. Please try again later.'
        } else if (error.response?.data?.detail) {
          this.errorMessage = error.response.data.detail
        } else {
          this.errorMessage = 'Error reopening rule vote'
        }
        this.showError = true
      }
    },
    getItemClass(item: Rule) {
      return item.version !== this.project.version ? 'disabled-row' : ''
    },
    async checkVotingStatus() {
      try {
        // Recarregar as regras para atualizar o estado
        await this.loadRules()
      } catch (error) {
        console.error('Error checking voting status:', error)
      }
    }
  }
})
</script>

<style scoped>
.v-data-table ::v-deep tbody tr {
  min-height: 80px !important;
}

.v-data-table ::v-deep td {
  padding-top: 10px !important;
  padding-bottom: 10px !important;
}

.status-container {
  padding: 5px 0;
}

.actions-container {
  padding: 5px 0;
}

.description-container {
  max-width: 300px;
}

.description-text {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: normal;
  line-height: 1.4;
}

.description-text.expanded {
  -webkit-line-clamp: initial;
  max-height: none;
}

.disabled-row {
  opacity: 0.6;
  pointer-events: none;
}
</style> 