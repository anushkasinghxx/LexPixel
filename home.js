/* script.js */
function analyzeText() {
  const text = document.getElementById("legalText").value;
  const output = document.getElementById("output");
  output.innerHTML = "";

  const words = text.split(" ").map(word => {
    let className = "none-risk";
    if (/penalty|violation|fine/.test(word.toLowerCase())) className = "high-risk";
    else if (/subject to|hereby|notwithstanding/.test(word.toLowerCase())) className = "medium-risk";
    else if (/at discretion|may/.test(word.toLowerCase())) className = "bias-risk";

    return `<span class='pixel-risk ${className}' title='${word}'></span>`;
  });

  output.innerHTML = words.join("");
}
