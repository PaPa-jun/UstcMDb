function likeReview(reviewId, writerID, reviewURL) {
    fetch(reviewURL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ review_id: reviewId, writer_id : writerID})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('like-count-' + reviewId).textContent = data.likes;
        } else {
            alert('请勿重复点赞');
        }
    });
}
