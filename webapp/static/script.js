// Update clock time every minute
function updateClock() {
    const now = new Date();
    const pad = n => String(n).padStart(2, '0');
    const hours = now.getHours();
    const mins = pad(now.getMinutes());
    document.getElementById('time').textContent = hours + ':' + mins;
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    const localeDate = now.toLocaleDateString('fr-FR', options);
    document.getElementById('date').textContent = localeDate;
}
updateClock();
setInterval(updateClock, 1000 * 30);
