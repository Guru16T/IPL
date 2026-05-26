const homeModal = document.getElementById("homeModal")

homeModal.addEventListener('show.bs.modal', function(event){

    const button = event.relatedTarget

    const teamName = button.getAttribute('data-team-name')
    const teamLogo = button.getAttribute('data-team-logo')
    const teamBg = button.getAttribute('data-team-bg')
    const teamId = button.getAttribute('data-team-id')

    document.getElementById("teamName").innerHTML = teamName
    document.getElementById("teamLogo").src = teamLogo
    document.getElementById("team_id").href = teamId

    let bgImg = document.getElementById("modalBg")

    bgImg.style.backgroundImage = `url('${teamBg}')`
    bgImg.style.backgroundSize = "cover"
    bgImg.style.backgroundRepeat = "no-repeat"
    bgImg.style.height = "60vh"
})