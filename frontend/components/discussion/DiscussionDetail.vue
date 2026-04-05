<template>
  <v-card>
    <v-toolbar
      dense
      flat
      color="primary"
      dark
    >
      <v-btn 
        icon
        @click="$router.go(-1)"
      >
        <v-icon color="white">{{ mdiArrowLeft }}</v-icon>
      </v-btn>
      <v-toolbar-title>
        {{ discussion ? discussion.name : 'Discussion' }}
        <v-chip
          v-if="discussion"
          :color="statusColor"
          small
          class="ml-2"
        >
          {{ discussion.status }}
        </v-chip>
      </v-toolbar-title>
      
      <v-spacer />
      
      <div v-if="discussion" class="text-caption mr-4">
        <div><small>Created: {{ formatDate(discussion.createdAt) }}</small></div>
        <div v-if="discussion.updatedAt !== discussion.createdAt">
          <small>Updated: {{ formatDate(discussion.updatedAt) }}</small>
        </div>
      </div>
      
      <v-tooltip v-if="discussion && isAdmin && isCurrentVersion" bottom>
        <template #activator="{ on, attrs }">
          <v-btn
            :color="discussion.status === 'open' ? 'error' : 'success'"
            dark
            small
            v-bind="attrs"
            class="mr-2 d-flex align-center justify-center"
            style="text-transform: none; min-width: 90px;"
            v-on="on"
            @click="toggleStatus"
          >
            <v-icon small class="mr-1">
              {{ discussion.status === 'open' ? 'mdi-close-circle' : 'mdi-check-circle' }}
            </v-icon>
            {{ discussion.status === 'open' ? 'Close' : 'Reopen' }}
          </v-btn>
        </template>
        <span>
          {{ discussion.status === 'open' ? 'Close Discussion' : 'Reopen Discussion' }}
        </span>
      </v-tooltip>
    </v-toolbar>

    <v-card-text>
      <div v-if="loading" class="text-center py-5">
        <v-progress-circular indeterminate color="primary" />
      </div>
      
      <template v-else>
        <div
          ref="messagesContainer"
          class="messages-container pa-2"
          style="height: 400px; overflow-y: auto; background-color: #f5f5f5;"
        >
          <div v-if="messages.length === 0" class="text-center pa-5 grey--text">
            No messages yet. Start the conversation!
          </div>
          
          <template v-else>
            <div
              v-for="message in messages"
              :key="message.id"
              class="mb-3"
              :class="{ 'ml-auto': isSentByCurrentUser(message) }"
              style="max-width: 70%;"
            >
              <v-card
                :color="isSentByCurrentUser(message) ? 'primary' : 'white'"
                :dark="isSentByCurrentUser(message)"
                :elevation="1"
              >
                <v-card-text>
                  <div class="d-flex align-center">
                    <v-avatar
                      size="28"
                      :color="getUserColor(message.senderUsername)"
                      class="mr-2"
                    >
                      <span class="white--text">{{ getUserInitial(message.senderUsername) }}</span>
                    </v-avatar>
                    <strong>{{ message.senderUsername }}</strong>
                    <small class="ml-2 grey--text" :class="{ 'text--lighten-3': isSentByCurrentUser(message) }">
                      {{ formatDate(message.createdAt) }}
                    </small>
                  </div>
                  <div class="mt-1">{{ message.content }}</div>
                </v-card-text>
              </v-card>
              
              <div v-if="canDeleteMessage(message)" class="d-flex justify-end mt-1">
                <v-btn x-small text color="error" @click="deleteMessage(message)">
                  <v-icon small>mdi-delete</v-icon>
                </v-btn>
              </div>
            </div>
          </template>
        </div>
        
        <v-divider class="my-2" />
        
        <div class="message-input">
          <v-form @submit.prevent="sendMessage">
            <v-row>
              <v-col cols="12">
                <v-textarea
                  v-model="newMessage"
                  label="Type a message"
                  rows="2"
                  auto-grow
                  :disabled="!discussion || discussion.status === 'closed' || !webSocketConnected"
                  append-icon="mdi-send"
                  @click:append="sendMessage"
                  @keydown.enter.prevent="sendMessage"
                />
              </v-col>
            </v-row>
          </v-form>
        </div>
      </template>
    </v-card-text>
  </v-card>
</template>

<script>
import { mdiArrowLeft } from '@mdi/js'
import { DiscussionMessage } from '~/domain/models/discussion/discussion'

export default {
  props: {
    projectId: {
      type: String,
      required: true
    },
    discussionId: {
      type: String,
      required: true
    }
  },
  
  data() {
    return {
      discussion: null,
      messages: [],
      loading: false,
      newMessage: '',
      socket: null,
      webSocketConnected: false,
      connectionRetries: 0,
      maxRetries: 3,
      pollingInterval: null,
      userColors: {}, // Mapa para armazenar as cores aleatórias para cada usuário neste chat
      availableColors: [
        'red', 'pink', 'purple', 'deep-purple', 
        'indigo', 'blue', 'light-blue', 'cyan', 
        'teal', 'green', 'light-green', 'lime',
        'amber', 'orange', 'deep-orange', 'brown'
      ], // Lista de cores disponíveis
      isAdmin: false,
      mdiArrowLeft
    }
  },
  
  computed: {
    currentUser() {
      return this.$store.getters['auth/getUser']
    },
    
    currentProject() {
      return this.$store.getters['projects/currentProject']
    },
    
    statusColor() {
      return this.discussion?.status === 'open' ? 'green' : 'grey'
    },
    
    isCurrentVersion() {
      return this.discussion && this.currentProject && 
             this.discussion.projectVersion === this.currentProject.version
    },
    
    wsUrl() {
      // Usar a função global que define a URL correta do WebSocket
      if (window.getWebSocketUrl) {
        return window.getWebSocketUrl(this.projectId, this.discussionId);
      }
      
      // Fallback para a implementação original se a função global não estiver disponível
      const API_URL = process.env.API_URL || 'http://127.0.0.1:8000';
      const host = API_URL.replace(/^https?:\/\//, '');
      const protocol = API_URL.startsWith('https') ? 'wss:' : 'ws:';
      
      console.log(`Fallback: Usando backend em ${API_URL} para WebSocket`);
      return `${protocol}//${host}/ws/projects/${this.projectId}/discussions/${this.discussionId}/`;
    }
  },
  
  async mounted() {
    // Check admin permissions
    try {
      const member = await this.$repositories.member.fetchMyRole(this.projectId)
      this.isAdmin = member.isProjectAdmin
    } catch (error) {
      console.error('Error fetching user role:', error)
      this.isAdmin = false
    }
    
    // Ensure current project is loaded
    await this.$store.dispatch('projects/setCurrentProject', this.projectId)
    
    this.fetchDiscussion();
    this.fetchMessages();
    this.connectWebSocket();
  },
  
  beforeDestroy() {
    this.disconnectWebSocket();
  },
  
  methods: {
    connectWebSocket() {
      if (this.connectionRetries >= this.maxRetries) {
        console.error('Max WebSocket connection retries reached');
        alert('Could not establish a real-time connection. Messages will not update automatically.');
        this.startPolling(); // Fallback para polling quando o WebSocket falhar
        return;
      }
      
      try {
        // Garantir que as mensagens são carregadas antes de conectar o WebSocket
        this.fetchMessages().then(() => {
          // Remover mensagens temporárias antigas ao reconectar
          this.messages = this.messages.filter(m => !m.id.toString().startsWith('temp_'));
          
          // Adicionar cookies automáticos para autenticação
          const wsUrl = this.wsUrl;
          console.log('Connecting to WebSocket:', wsUrl);
          
          // Criar conexão WebSocket
          this.socket = new WebSocket(wsUrl);
          
          this.socket.onopen = () => {
            console.log('WebSocket connected successfully');
            this.webSocketConnected = true;
            this.connectionRetries = 0;
            
            // Se tínhamos um polling funcionando, podemos parar
            if (this.pollingInterval) {
              this.stopPolling();
            }
          };
          
          this.socket.onmessage = (event) => {
            console.log('WebSocket message received:', event.data);
            try {
              const data = JSON.parse(event.data);
              
              // Verificar se há erro
              if (data.error) {
                console.error('WebSocket error message:', data.error);
                alert(`Error: ${data.error}`);
                return;
              }
              
              // Processar mensagem recebida
              if (data.message) {
                // Add the new message to our list
                const newMessage = new DiscussionMessage(
                  data.message.id,
                  data.message.discussion,
                  data.message.sender,
                  data.message.sender_username,
                  data.message.content,
                  data.message.created_at
                );
                
                // Verificar se é uma mensagem temporária que enviamos
                const tempMessageIndex = this.messages.findIndex(m => 
                  (m.id.toString().startsWith('temp_') && 
                   m.content === newMessage.content && 
                   m.sender === newMessage.sender)
                );
                
                if (tempMessageIndex >= 0) {
                  // Substituir a mensagem temporária pela mensagem real
                  console.log('Substituindo mensagem temporária pelo ID real:', newMessage.id);
                  this.$set(this.messages, tempMessageIndex, newMessage);
                  
                  // Reordenar as mensagens por data de criação
                  this.messages = this.messages.sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt));
                } else if (!this.messages.some(m => m.id === newMessage.id)) {
                  // Adicionar apenas se não for uma mensagem duplicada
                  this.messages.push(newMessage);
                  
                  // Reordenar as mensagens por data de criação
                  this.messages = this.messages.sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt));
                  
                  this.$nextTick(() => {
                    this.scrollToBottom();
                  });
                }
              }
            } catch (e) {
              console.error('Error parsing WebSocket message:', e);
            }
          };
          
          this.socket.onclose = (event) => {
            console.log('WebSocket disconnected:', event);
            this.webSocketConnected = false;
            
            // Se WebSocket caiu, podemos começar o polling
            this.startPolling();
            
            // Try to reconnect after a delay
            setTimeout(() => {
              this.connectionRetries++;
              this.connectWebSocket();
            }, 3000);
          };
          
          this.socket.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.webSocketConnected = false;
            
            // Se WebSocket tem erro, usamos polling
            this.startPolling();
          };
        });
      } catch (error) {
        console.error('Error connecting to WebSocket:', error);
        this.webSocketConnected = false;
        
        // Ainda assim, carregamos as mensagens via REST API
        this.startPolling();
      }
    },
    
    // Implementação de polling para quando o WebSocket falhar
    startPolling() {
      // Evitar múltiplos intervals
      if (this.pollingInterval) {
        return;
      }
      
      console.log("Iniciando polling de mensagens...");
      this.pollingInterval = setInterval(() => {
        this.fetchMessages();
      }, 3000);
    },
    
    stopPolling() {
      if (this.pollingInterval) {
        console.log("Parando polling de mensagens...");
        clearInterval(this.pollingInterval);
        this.pollingInterval = null;
      }
    },
    
    disconnectWebSocket() {
      if (this.socket) {
        this.socket.close();
        this.socket = null;
        this.webSocketConnected = false;
      }
    },
    
    async fetchDiscussion() {
      this.loading = true
      try {
        if (!this.projectId || !this.discussionId) return
        
        this.discussion = await this.$services.discussion.getDiscussion(this.projectId, this.discussionId)
        
        // Fetch messages
        if (this.discussion) {
          await this.fetchMessages()
        }
      } catch (error) {
        console.error('Error fetching discussion:', error)
        if (error.response && error.response.status === 500) {
          alert('Database unavailable, please come back later.')
        }
      } finally {
        this.loading = false
      }
    },
    
    async fetchMessages() {
      try {
        if (!this.projectId || !this.discussionId) return
        
        this.messages = await this.$services.discussion.getMessages(this.projectId, this.discussionId)
        this.scrollToBottom()
      } catch (error) {
        console.error('Error fetching messages:', error)
        if (error.response && error.response.status === 500) {
          alert('Database unavailable, please come back later.')
        }
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString()
    },
    
    async sendMessage() {
      try {
        if (!this.newMessage.trim() || !this.discussion || this.discussion.status === 'closed') {
          return
        }
        
        const message = new DiscussionMessage(
          0,
          this.discussionId,
          this.currentUser.id,
          this.currentUser.username,
          this.newMessage,
          new Date().toISOString()
        )
        
        // If using WebSocket
        if (this.webSocketConnected) {
          this.sendMessageWebSocket(message)
        } else {
          // Fallback to REST API
          await this.$services.discussion.createMessage(this.projectId, this.discussionId, message)
          await this.fetchMessages()
        }
        
        this.newMessage = ''
      } catch (error) {
        console.error('Error sending message:', error)
        if (error.response && error.response.status === 500) {
          alert('Database unavailable, please come back later.')
        }
      }
    },
    
    async toggleStatus() {
      try {
        if (!this.discussion) return
        
        const newStatus = this.discussion.status === 'open' ? 'closed' : 'open'
        const updatedDiscussion = { ...this.discussion, status: newStatus }
        
        await this.$services.discussion.updateDiscussion(this.projectId, updatedDiscussion)
        this.discussion.status = newStatus
        alert(`Discussion ${newStatus}`)
      } catch (error) {
        console.error('Error updating discussion status:', error);
        // Check for any indication of a 500 error
        if (error?.response?.status === 500 || 
            error?.message?.includes('500') || 
            error?.toString().includes('500')) {
          alert('Database unavailable. Please try again later');
        }
      }
    },
    
    async deleteMessage(message) {
      try {
        if (!message || !message.id) return
        
        await this.$services.discussion.deleteMessage(this.projectId, this.discussionId, message.id)
        
        // Remove from local list
        const index = this.messages.findIndex(m => m.id === message.id)
        if (index !== -1) {
          this.messages.splice(index, 1)
        }
      } catch (error) {
        console.error('Error deleting message:', error)
        if (error.response && error.response.status === 500) {
          alert('Database unavailable, please come back later.')
        }
      }
    },
    
    isSentByCurrentUser(message) {
      return message.sender === this.currentUser.id || message.senderUsername === this.currentUser.username
    },
    
    canDeleteMessage(message) {
      // Allow users to delete their own messages or admins to delete any message
      return this.isSentByCurrentUser(message) || this.isAdmin
    },
    
    scrollToBottom() {
      const container = this.$refs.messagesContainer
      if (container) {
        container.scrollTop = container.scrollHeight
      }
    },
    
    getUserInitial(username) {
      if (!username) return '?'
      return username.charAt(0).toUpperCase()
    },
    
    getUserColor(username) {
      if (!username) return 'grey'
      
      // Se este usuário já tem uma cor atribuída, use-a
      if (this.userColors[username]) {
        return this.userColors[username]
      }
      
      // Se não há mais cores disponíveis, reinicie a lista de cores disponíveis
      if (this.availableColors.length === 0) {
        this.availableColors = [
          'red', 'pink', 'purple', 'deep-purple', 
          'indigo', 'blue', 'light-blue', 'cyan', 
          'teal', 'green', 'light-green', 'lime',
          'amber', 'orange', 'deep-orange', 'brown'
        ]
      }
      
      // Escolher uma cor aleatória da lista de cores disponíveis
      const randomIndex = Math.floor(Math.random() * this.availableColors.length)
      const selectedColor = this.availableColors[randomIndex]
      
      // Remover a cor escolhida da lista de disponíveis
      this.availableColors.splice(randomIndex, 1)
      
      // Armazenar a cor para este usuário
      this.userColors[username] = selectedColor
      
      return selectedColor
    },
    
    sendMessageWebSocket(message) {
      if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
        console.warn('WebSocket not connected, using REST API fallback')
        // Fallback to REST API
        this.$services.discussion.createMessage(this.projectId, this.discussionId, message)
          .then(() => this.fetchMessages())
          .catch(error => console.error('Error sending message via API:', error))
        return
      }
      
      try {
        // Create a temporary ID for this message to identify it when the server responds
        const tempId = `temp_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
        
        // Add a temporary message to the UI immediately
        const tempMessage = new DiscussionMessage(
          tempId,
          this.discussionId,
          this.currentUser.id,
          this.currentUser.username,
          message.content,
          new Date().toISOString()
        )
        
        this.messages.push(tempMessage)
        this.$nextTick(() => {
          this.scrollToBottom()
        })
        
        // Send the message via WebSocket - with the correct format for the backend consumer
        const payload = {
          content: message.content
        }
        
        this.socket.send(JSON.stringify(payload))
        console.log('Message sent via WebSocket:', payload)
      } catch (error) {
        console.error('Error sending message via WebSocket:', error)
        // Fallback to REST API if WebSocket fails
        this.$services.discussion.createMessage(this.projectId, this.discussionId, message)
          .then(() => this.fetchMessages())
          .catch(error => console.error('Error sending message via API:', error))
      }
    }
  }
}
</script> 