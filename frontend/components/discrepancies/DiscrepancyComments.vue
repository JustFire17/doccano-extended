<template>
  <div>
    <div class="comments-list">
      <ul>
        <li v-for="comment in comments" :key="comment.id">
          <span style="font-size: 0.8em; color: #888;">({{ formatDate(comment.created_at) }})</span>
          <b> {{ comment.user_username }}:</b> {{ comment.content }}
        </li>
      </ul>
    </div>
    <form class="comment-form" @submit.prevent="addComment">
      <input class="comment-input" v-model="newComment" placeholder="Write a comment..." required />
      <button class="comment-btn" type="submit">Comment</button>
    </form>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, watch } from 'vue';
import { getDiscrepancyComments, postDiscrepancyComment } from '@/repositories/discrepancy/apiDiscrepancyCommentRepository';

export default defineComponent({
  name: 'DiscrepancyComments',
  props: {
    discrepancyId: {
      type: Number,
      required: true
    }
  },
  setup(props) {
    const comments = ref<any[]>([]);
    const newComment = ref('');

    const fetchComments = async () => {
      try {
        const { data } = await getDiscrepancyComments(props.discrepancyId);
        comments.value = data;
      } catch (error: any) {
        console.error('Error fetching comments:', error);
        let message = "Sorry, we couldn't load the comments right now. Please try again in a few moments.";
        if (error.response?.data?.detail) {
          message = error.response.data.detail;
        }
        alert(message);
      }
    };

    const addComment = async () => {
      if (!newComment.value.trim()) return;
      try {
        await postDiscrepancyComment(props.discrepancyId, newComment.value);
        newComment.value = '';
        await fetchComments();
      } catch (error: any) {
        console.error('Error adding comment:', error);
        let message = "Sorry, we couldn't add your comment right now. Please try again in a few moments.";
        if (error.response?.data?.detail) {
          message = error.response.data.detail;
        }
        alert(message);
      }
    };

    const formatDate = (dateString: string) => {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleString('pt-PT');
    };

    onMounted(fetchComments);
    watch(() => props.discrepancyId, fetchComments);

    return { comments, newComment, addComment, formatDate };
  }
});
</script>

<style scoped>
.comments-list {
  max-height: 250px;
  overflow-y: auto;
  margin-bottom: 1em;
}
.comment-form {
  display: flex;
  gap: 0.5em;
}
ul {
  list-style: none;
  padding: 0;
}
li {
  margin-bottom: 0.5em;
}
.comment-input {
  color: #fff;
  background: #222;
  border: 1px solid #444;
  border-radius: 4px;
  padding: 8px;
}
.comment-input::placeholder {
  color: #aaa;
}
.comment-btn {
  background: #1976d2;
  color: #fff;
  border: none;
  border-radius: 4px;
  padding: 8px 16px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.2s;
}
.comment-btn:hover {
  background: #1565c0;
}
</style> 