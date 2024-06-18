function likeReview(reviewId) {
    fetch('{{ movie.like_review }}', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ review_id: reviewId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('like-count').textContent = data.likes;
        } else {
            alert('点赞失败，请稍后再试。');
        }
    });
}
