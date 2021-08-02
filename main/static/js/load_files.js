let loadImage = function(event) {
    let section = document.getElementById('profile_pic_block');
    let output = "<img src = '" + URL.createObjectURL(event.target.files[0]) + "' id = 'profile_pic_preview'>";
    section.innerHTML = output;
};