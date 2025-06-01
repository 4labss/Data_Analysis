import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, CheckButtons
from scipy.signal import butter, filtfilt

class HarmonicVisualizer:
    def __init__(self):
        self.initial_params = {
            'amplitude': 1.0,
            'frequency': 0.3,
            'phase': 0.0,
            'noise_mean': 0.0,
            'noise_covariance': 0.15,
            'cutoff_frequency': 2.0,
            'show_noise': True
        }
        self.params = self.initial_params.copy()
        self.t = np.linspace(0, 10, 1000)
        self.harmonic = self._calculate_harmonic()
        self.noise = self._generate_noise()
        self._setup_plot()
        self._setup_widgets()
        self._update(None)

    def _calculate_harmonic(self):
        return self.params['amplitude'] * np.sin(
            2 * np.pi * self.params['frequency'] * self.t + self.params['phase']
        )

    def _generate_noise(self):
        return np.random.normal(
            self.params['noise_mean'],
            np.sqrt(self.params['noise_covariance']),
            len(self.t)
        )

    def _setup_plot(self):
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        plt.subplots_adjust(left=0.1, bottom=0.45)
        self.line_noisy, = self.ax.plot(self.t, self.harmonic + self.noise, lw=2, color='orange', label='Зашумлена гармоніка')
        self.line_clean, = self.ax.plot(self.t, self.harmonic, lw=2, color='blue', linestyle='--', label='Чиста гармоніка', visible=False)
        self.line_filtered, = self.ax.plot(self.t, self.harmonic, lw=2, color='purple', label='Відфільтрована гармоніка')
        self.ax.set_xlabel('Час (t)')
        self.ax.set_ylabel('Амплітуда (y)')
        self.ax.set_title('Інтерактивна гармоніка з шумом та фільтрацією')
        self.ax.grid(True)
        self.ax.legend()

    def _setup_widgets(self):
        ax_amp = plt.axes([0.15, 0.35, 0.65, 0.03])
        ax_freq = plt.axes([0.15, 0.30, 0.65, 0.03])
        ax_phase = plt.axes([0.15, 0.25, 0.65, 0.03])
        ax_noise_mean = plt.axes([0.15, 0.20, 0.65, 0.03])
        ax_noise_cov = plt.axes([0.15, 0.15, 0.65, 0.03])
        ax_cutoff = plt.axes([0.15, 0.10, 0.65, 0.03])

        self.slider_amp = Slider(ax_amp, 'Амплітуда', 0.1, 2.0, valinit=self.params['amplitude'])
        self.slider_freq = Slider(ax_freq, 'Частота', 0.1, 2.0, valinit=self.params['frequency'])
        self.slider_phase = Slider(ax_phase, 'Фаза', 0, 2 * np.pi, valinit=self.params['phase'])
        self.slider_noise_mean = Slider(ax_noise_mean, 'Середнє шуму', -0.5, 0.5, valinit=self.params['noise_mean'])
        self.slider_noise_cov = Slider(ax_noise_cov, 'Дисперсія шуму', 0, 0.5, valinit=self.params['noise_covariance'])
        self.slider_cutoff = Slider(ax_cutoff, 'Частота зрізу', 0.1, 10.0, valinit=self.params['cutoff_frequency'])

        self.slider_amp.on_changed(self._update)
        self.slider_freq.on_changed(self._update)
        self.slider_phase.on_changed(self._update)
        self.slider_noise_mean.on_changed(self._update)
        self.slider_noise_cov.on_changed(self._update)
        self.slider_cutoff.on_changed(self._update)

        ax_reset = plt.axes([0.8, 0.025, 0.1, 0.04])
        self.button_reset = Button(ax_reset, 'Reset', hovercolor='0.975')
        self.button_reset.on_clicked(self._reset)
        
        ax_check = plt.axes([0.05, 0.025, 0.2, 0.05])
        self.check_noise = CheckButtons(ax_check, ['Показати шум'], [self.params['show_noise']])
        self.check_noise.on_clicked(self._toggle_noise)

    def _update(self, event):
        new_params = {
            'amplitude': self.slider_amp.val,
            'frequency': self.slider_freq.val,
            'phase': self.slider_phase.val,
            'noise_mean': self.slider_noise_mean.val,
            'noise_covariance': self.slider_noise_cov.val,
            'cutoff_frequency': self.slider_cutoff.val
        }

        if (new_params['amplitude'] != self.params['amplitude'] or
            new_params['frequency'] != self.params['frequency'] or
            new_params['phase'] != self.params['phase']):
            self.params.update(new_params)
            self.harmonic = self._calculate_harmonic()

        if (new_params['noise_mean'] != self.params['noise_mean'] or
            new_params['noise_covariance'] != self.params['noise_covariance']):
            self.params.update(new_params)
            self.noise = self._generate_noise()

        self.params.update(new_params)

        noisy_signal = self.harmonic + self.noise
        self.line_noisy.set_ydata(noisy_signal)
        self.line_clean.set_ydata(self.harmonic)
        self._update_filter(noisy_signal)
        self.fig.canvas.draw_idle()

    def _update_filter(self, noisy_signal):
        fs = 1 / (self.t[1] - self.t[0])
        cutoff = self.params['cutoff_frequency']
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        b, a = butter(N=5, Wn=normal_cutoff, btype='low', analog=False)
        filtered_signal = filtfilt(b, a, noisy_signal)
        self.line_filtered.set_ydata(filtered_signal)

    def _reset(self, event):
        self.slider_amp.reset()
        self.slider_freq.reset()
        self.slider_phase.reset()
        self.slider_noise_mean.reset()
        self.slider_noise_cov.reset()
        self.slider_cutoff.reset()

    def _toggle_noise(self, label):
        self.params['show_noise'] = not self.params['show_noise']
        self.line_noisy.set_visible(self.params['show_noise'])
        self.line_clean.set_visible(not self.params['show_noise'])
        self.fig.canvas.draw_idle()

    def run(self):
        plt.show()

if __name__ == '__main__':
    visualizer = HarmonicVisualizer()
    visualizer.run()
