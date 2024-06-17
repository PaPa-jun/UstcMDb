document.addEventListener('DOMContentLoaded', function () {
    const submitButton = document.querySelector('.comments_to_write button[type="submit"]');
    const commentTextArea = document.querySelector('.comments_to_write textarea');
    const newCommentContainer = document.getElementById('comments_history');

    submitButton.addEventListener('click', function (event) {
        event.preventDefault();

        const commentText = commentTextArea.value.trim();

        if (commentText !== '') {
            const newCommentHTML = `
                <div class="single_comment">
                    <table class="writer_info">
                        <tbody>
                            <tr>
                                <td class="writer_profile">
                                    <a href="#">
                                        <img src="{{ url_for('static', filename=g.current_user.avatar) }}" alt="评论者图片" width="100px">
                                    </a>
                                </td>
                                <td class="writer_name">
                                    <a href="#">{{ g.current_user.username }}</a>
                                    <span style="color: grey;">我</span>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                    <div class="review_content">
                        ${commentText}
                    </div>
                    <div class="comment_footer">
                        <div class="comment_date">
                            <span> 刚刚 </span>
                        </div>
                        <div class="comment_likes">
                            <button class="like-button">点赞</button>
                            <span class="like-count"> 0 </span>
                        </div>
                        <div class="reply_button">
                            <button class="reply-button">回复</button>
                        </div>
                    </div>
                    <div class="reply"></div>
                </div>
            `;

            newCommentContainer.insertAdjacentHTML('afterbegin', newCommentHTML);

            commentTextArea.value = '';
            fetch('/submit_comment', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ comment: commentText })
            })
                .then(response => response.json())
                .then(data => {
                    console.log('评论已提交到数据库:', data);
                })
                .catch(error => {
                    console.error('提交评论时出错:', error);
                    alert('提交评论时出错，请稍后再试。');
                });
        }
    });

    newCommentContainer.addEventListener('click', function (event) {
        if (event.target.classList.contains('like-button')) {
            const likeCountSpan = event.target.nextElementSibling;
            let likeCount = parseInt(likeCountSpan.textContent);
            likeCountSpan.textContent = likeCount + 1;
        } else if (event.target.classList.contains('reply-button')) {
            const replyContainer = event.target.closest('.single_comment').querySelector('.reply');
            const replyTextArea = document.createElement('textarea');
            const replySubmitButton = document.createElement('button');
            replySubmitButton.textContent = '提交回复';

            replyContainer.appendChild(replyTextArea);
            replyContainer.appendChild(replySubmitButton);

            replySubmitButton.addEventListener('click', function () {
                const replyText = replyTextArea.value.trim();
                if (replyText !== '') {
                    const newReplyHTML = `<div class="single_reply">${replyText}</div>`;
                    replyContainer.insertAdjacentHTML('beforeend', newReplyHTML);
                    replyTextArea.remove();
                    replySubmitButton.remove();
                }
            });
        }
    });
});
