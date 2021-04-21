document.addEventListener("DOMContentLoaded", () => {
  const log = console.log,
    array = ["../static/uploads/pika.png","../static/css/snorlax.png",
        "../static/css/bulbasaur.png","../static/css/poliwhirl.png",
        "../static/css/mewtwo.png","../static/css/charmander.png",
        ,"../static/css/evee.png"]
    random = Math.floor(Math.random() * array.length),
    target = document.getElementById("char");
  target.src = `${array[random]}`;
  log(target);
});