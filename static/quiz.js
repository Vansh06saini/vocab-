function loadQuestion() {
    if (currentIndex >= questions.length) {
        alert(`🎯 Quiz finished! Your total score: ${userScore}`);
        window.location.href = "/index";
        return;
    }

    const q = questions[currentIndex];
    document.getElementById('question-text').textContent =
        `Q${currentIndex + 1}. What is the ${q.label} of "${q.word}"?`;

    const buttons = document.querySelectorAll('.qz-option');
    buttons.forEach((btn, i) => {
        const optionText = q.options[i];
        if (!optionText) {
            btn.style.display = 'none';
            return;
        }

        btn.style.display = 'block';
        btn.textContent = `${String.fromCharCode(65 + i)}. ${optionText}`;
        btn.disabled = false;
        btn.classList.remove('correct', 'wrong');

        btn.onclick = () => checkAnswer(btn, optionText, q.correct);
    });
}

function checkAnswer(clickedButton, chosenAnswer, correctAnswer) {
    const buttons = document.querySelectorAll('.qz-option');
    buttons.forEach(b => b.disabled = true);

    if (chosenAnswer === correctAnswer) {
        clickedButton.classList.add('correct');
        userScore += 5;
    } else {
        clickedButton.classList.add('wrong');
        userScore -= 1;
        buttons.forEach(b => {
            if (b.textContent.includes(correctAnswer)) {
                b.classList.add('correct');
            }
        });
    }

    document.getElementById('score-display').textContent = userScore;

    fetch("/quiz/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            question_index: currentIndex,
            correct: chosenAnswer === correctAnswer
        })
    }).catch(err => console.error("Error submitting:", err));
}

document.querySelector('.qz-next-btn').addEventListener('click', () => {
    const answered = Array.from(document.querySelectorAll('.qz-option'))
        .some(btn => btn.classList.contains('correct') || btn.classList.contains('wrong'));

    if (!answered) {
        alert("⚠ Please select an option first!");
        return;
    }

    currentIndex++;
    loadQuestion();
});
