function formatTimestamp(date = new Date()) {
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  const hh = String(date.getHours()).padStart(2, '0')
  const mm = String(date.getMinutes()).padStart(2, '0')
  const ss = String(date.getSeconds()).padStart(2, '0')
  return `${y}-${m}-${d} ${hh}:${mm}:${ss}`
}

function jitter(base, delta) {
  return Number((base + (Math.random() - 0.5) * delta).toFixed(2))
}

export function buildMockTelemetryPayload() {
  return {
    timestamp: formatTimestamp(),
    system_status: {
      mode: 'AUTO',
      signal_source: 'SAT-A',
      source_status: 'normal',
      lock_status: 'locked',
      lock_indicator: 'green'
    },
    signal_params: {
      agc_threshold: 1.2,
      agc_voltage: 3.5,
      azimuth_error_voltage: 0.02,
      pitch_error_voltage: 0.01
    },
    tracking_data: {
      turntable_system: {
        guide_azimuth: jitter(120.5, 6),
        guide_pitch: jitter(45, 1),
        guide_tilt: 0,
        current_azimuth: jitter(120.4, 4),
        current_pitch: jitter(45, 1),
        current_tilt: 0,
        deviation_azimuth: jitter(0, 0.2),
        deviation_pitch: jitter(0, 0.2),
        deviation_tilt: jitter(0, 0.2)
      },
      geodetic_system: {
        guide_azimuth: jitter(110.2, 6),
        guide_pitch: jitter(40, 1),
        current_azimuth: jitter(110.1, 4),
        current_pitch_alt: jitter(40, 1),
        deviation_azimuth: jitter(0, 0.2),
        deviation_pitch: jitter(0, 0.2)
      }
    },
    motor_diagnostics: {
      motor_1: {
        power_on: true,
        status: 'running',
        current: jitter(5.2, 0.5),
        voltage: jitter(220, 8),
        inertia: 0.85,
        temp: jitter(42.5, 2)
      },
      motor_2: {
        power_on: true,
        status: 'standby',
        current: jitter(0.1, 0.1),
        voltage: jitter(220, 8),
        inertia: 0.85,
        temp: jitter(38, 2)
      }
    }
  }
}
