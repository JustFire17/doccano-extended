/**
 * Funções de configuração de WebSocket para o Doccano
 */

// Evitar mensagens de teste automáticas do WebSocket
window.DISABLE_TEST_MESSAGES = true;

// Sobrescreve a URL do WebSocket para usar o servidor Nginx em vez do backend diretamente
window.getWebSocketUrl = function(projectId, discussionId) {
  // Determinar o protocolo com base no protocolo HTTP atual
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  
  // Construir URL relativa
  return `${protocol}//${window.location.host}/ws/projects/${projectId}/discussions/${discussionId}/`;
}

// Função para garantir que as mensagens são ordenadas corretamente
window.sortDiscussionMessages = function(messages) {
  if (!messages || !Array.isArray(messages)) return [];
  return messages.sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt));
} 