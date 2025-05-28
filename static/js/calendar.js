document.addEventListener('DOMContentLoaded', function () {
  const calendarEl = document.getElementById('calendar');
  if (!calendarEl) {
    console.log('No hay elemento #calendar en esta página, no se carga el calendario');
    return;
  }

  const rolUsuario = calendarEl.dataset.rol;

  const calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: 'dayGridMonth',
    locale: 'es',
    headerToolbar: {
      left: 'prev,next today',
      center: 'title',
      right: 'dayGridMonth,timeGridWeek,listWeek'
    },
    navLinks: true,
    editable: rolUsuario === 'profesor',
    selectable: rolUsuario === 'profesor',
    selectMirror: rolUsuario === 'profesor',
    eventSources: [
      {
        url: '/api/actividades',
        method: 'GET',
        failure: () => alert('Error al cargar las actividades'),
      }
    ],
    dateClick: function (info) {
      if (rolUsuario === 'profesor') {
        window.location.href = `/actividad/nueva?fecha=${info.dateStr}`;
      }
    },
    eventClick: function (info) {
      info.jsEvent.preventDefault();
      const id = info.event.id;
      if (rolUsuario === 'profesor') {
        window.location.assign(`/editar/${id}`);
      } else {
        // Abrir el PDF en la carpeta /pdfs
        const urlPdf = `/pdfs/actividad_${id}.pdf`;
        window.open(urlPdf, '_blank'); // abrir en nueva pestaña
      }
    },

    /*eventClick: function (info) {
      info.jsEvent.preventDefault();
      const id = info.event.id;
      //window.location.assign(`/editar/${id}`); Esto hace que al hacer click en una actividad te lleve a editar la actividad
      window.open(`/actividad/pdf/${id}`, '_blank');
    },*/
    eventDrop: function (info) {
      if (rolUsuario !== 'profesor') {
        info.revert();
        return;
      }
      const id = info.event.id;
      const nuevaFecha = info.event.startStr;

      fetch(`/api/actividad/${id}/mover`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ fecha: nuevaFecha })
      })
      .then(response => {
        if (!response.ok) throw new Error('Error al mover la actividad');
      })
      .catch(error => {
        alert(error.message);
        info.revert();
      });
    },

    datesSet: function (dateInfo) {
      const headerTitleEl = calendarEl.querySelector('.fc-toolbar-title');
      if (headerTitleEl) {
        let title = headerTitleEl.textContent.trim(); // "mayo 2025"
        let parts = title.split(' '); // ["mayo", "2025"]
        if (parts.length === 2) {
          let mes = parts[0];
          let año = parts[1];
          mes = mes.charAt(0).toUpperCase() + mes.slice(1).toLowerCase();
          headerTitleEl.textContent = mes + ' ' + año;
        }
      }
    }
  });

  calendar.render();
});
