export default function ({ $axios, _redirect, store }) {
  $axios.onError(error => {
    console.error('API Error:', error);
    
    // Handle server errors (500)
    if (error.response && error.response.status === 500) {
      // Show alert only for user-initiated actions, not for background API calls
      // We could enhance this with custom headers to identify user-initiated actions
      
      const errorMessage = 'Database unavailable, please come back later.';
      
      // Check if we've already shown an error recently (to prevent multiple alerts)
      const lastErrorTime = store.state.lastErrorAlertTime || 0;
      const currentTime = Date.now();
      
      // Only show one error alert every 5 seconds
      if (currentTime - lastErrorTime > 5000) {
        alert(errorMessage);
        
        // Store the time we showed the alert
        store.commit('setLastErrorAlertTime', currentTime);
      }
    }
    
    // Forward the error so individual components can still handle specific cases
    return Promise.reject(error);
  });
} 