// static/scripts.js

document.getElementById('comment-form').addEventListener('submit', function(event) {
    event.preventDefault();  // 阻止表单提交的默认行为

    const commentText = document.getElementById('comment-text').value;
    if (commentText.trim() === '') return;

    const comment = {
        id: Date.now(),
        text: commentText
    };

    addCommentToDOM(comment);
    document.getElementById('comment-text').value = '';
});

function addCommentToDOM(comment) {
    const commentsSection = document.getElementById('comments-section');

    const commentDiv = document.createElement('div');
    commentDiv.className = 'comment';
    commentDiv.id = `comment-${comment.id}`;
    commentDiv.innerHTML = `<p>${comment.text}</p>`;

    commentsSection.appendChild(commentDiv);
}

