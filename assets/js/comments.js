document.addEventListener('DOMContentLoaded', () => {
    // 使用事件委托来绑定点击事件
    document.body.addEventListener('click', (event) => {
        // 检查点击的目标是否是 .reply_button_main 内的 button 元素
        if (event.target && event.target.matches('.reply_button_main')) {
            // 找到最近的 .single_comment 元素并获取其中的 .reply-form 表单
            var replyForm = event.target.closest('.single_comment').querySelector('.reply-form');
            // 切换 reply-form 表单的显示状态
            replyForm.style.display = replyForm.style.display === 'block' ? 'none' : 'block';
        }

        // 检查点击的目标是否是 .reply_button_sub 内的 button 元素
        if (event.target && event.target.matches('.reply_button_sub')) {
            // 找到最近的 .sub_reply 元素并获取其中的 .reply-form-b 表单
            var replyForm = event.target.closest('.sub_reply').querySelector('.reply-form-b');
            // 切换 reply-form 表单的显示状态
            replyForm.style.display = replyForm.style.display === 'block' ? 'none' : 'block';
        }
    });

    document.body.addEventListener('submit', (event) => {
        // 检查提交的目标是否是 .reply-form 表单
        if (event.target && event.target.matches('.reply-form')) {
            event.preventDefault(); // 阻止表单默认提交
            handleReplyFormSubmit(event, 'single_comment', 'reply', 'reply-content', 'reply_button-b', 'reply-form');
        }

        if (event.target && event.target.matches('.reply-form-b')) {
            event.preventDefault(); // 阻止表单默认提交
            handleReplyFormSubmit(event, 'sub_reply', 'reply', 'reply-content', 'reply_button_sub', 'reply-form-b');
        }
    });
});

function handleReplyFormSubmit(event, commentClass, replyClass, replyContentClass, replyButtonClass, replyFormClass) {
    var replyForm = event.target;
    var replyContent = replyForm.querySelector('#content_text').value;
    var movieId = replyForm.querySelector('#movie_id').value;
    var writerId = replyForm.querySelector('#writer_id').value;
    var userId = replyForm.querySelector('#user_id').value;
    var reviewID = replyForm.querySelector('#review_id').value;

    if (replyContent.trim() === '') {
        replyForm.style.display = 'none';
        alert("评论内容不能为空！");
        return;
    }

    var replyDiv = event.target.closest(`.${commentClass}`).querySelector(`.${replyClass}`);
    var newReply = document.createElement('div');
    newReply.className = replyContentClass;
    newReply.innerHTML = `
        <table class="reply_header">
            <tbody>
                <tr>
                    <td class="reply_avatar">
                        <a href="{{ url_for('user.profile', username = g.current_user.username) }}">
                            {% if g.current_user.avatar %}
                            <img src="{{ url_for('static', filename=g.current_user.avatar) }}" alt="{{ g.current_user.username }}" class="user-avatar">
                            {% else %}
                            <img src="{{ url_for('static', filename='images/avatars/fixed_pics/default.jpg') }}" alt="{{ g.current_user.username }}" class="user-avatar">
                        {% endif %}
                        </a>
                    </td>
                    <td class="reply_username">
                        <a href="{{ url_for('user.profile', username = g.current_user.username) }}">
                            {{ g.current_user.username }}
                        </a>
                    </td>
                </tr>
            </tbody>
        </table>
        <div class="reply_text">${replyContent}</div>
        <div class="reply_footer">
            <div class="reply_date"><span> 刚刚 </span></div>
            <div class="reply_likes">
                <button class="like-button">点赞</button>
                <span class="like-count"> 0 </span>
            </div>
            {% if g.current_user %}
            <div class="${replyButtonClass}">
                <button class="reply-button" id="reply-button-level-b">回复</button>
            </div>
            {% else %}
            <div class="reply_button">
                <a href="{{ url_for('user.login') }}">回复</a>
            </div>
            {% endif %}
        </div>
    `;
    replyDiv.appendChild(newReply);
    event.target.querySelector('#content_text').value = '';
    replyForm.style.display = 'none';

    var xhr = new XMLHttpRequest();
    xhr.open('POST', '{{ url_for("movie.reply_comment") }}', true);
    xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
    xhr.send(JSON.stringify({
        movie_id: movieId,
        writer_id: writerId,
        user_id: userId,
        content: replyContent,
        review_id: reviewID
    }));

    xhr.onload = function () {
        if (!xhr.status === 200) {
            alert("回复没有提交到数据库");
        }
    };
}
