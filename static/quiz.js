document.addEventListener("DOMContentLoaded", () => {
    if (questions.length > 0) {
        loadQuestion();
    }
});

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

        btn.onclick = () => checkAnswer(btn, optionText, q.correct, q.word);
    });
}

function checkAnswer(clickedButton, chosenAnswer, correctAnswer, word) {
    const buttons = document.querySelectorAll('.qz-option');
    buttons.forEach(b => b.disabled = true);

    let isCorrect = false;
    if (chosenAnswer === correctAnswer) {
        clickedButton.classList.add('correct');
        userScore += 5;
        isCorrect = true;
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

    // Send result to backend
    fetch("/quiz/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            word: word.toLowerCase(),
            correct: isCorrect
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
