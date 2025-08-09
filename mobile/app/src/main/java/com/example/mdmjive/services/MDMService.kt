package com.example.mdmjive.services

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.app.admin.DevicePolicyManager
import android.content.Context
import android.content.Intent
import android.os.Build
import android.os.IBinder
import android.util.Log
import androidx.core.app.NotificationCompat
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import com.example.mdmjive.BuildConfig
import com.example.mdmjive.MainActivity
import com.example.mdmjive.R
import com.example.mdmjive.database.LogDatabase
import com.example.mdmjive.network.ApiServiceFactory
import com.example.mdmjive.repository.DeviceRepository
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import java.util.concurrent.TimeUnit

class MDMService : Service() {

    companion object {
        const val CHANNEL_ID = "mdm_service_channel"
        const val FOREGROUND_ID = 1
    }

    private lateinit var devicePolicyManager: DevicePolicyManager
    private lateinit var repository: DeviceRepository
    private lateinit var workManager: WorkManager
    private var job: Job? = null

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
        startForeground(FOREGROUND_ID, buildNotification())
        setupService()
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                getString(R.string.app_name),
                NotificationManager.IMPORTANCE_LOW
            )
            val manager = getSystemService(NotificationManager::class.java)
            manager.createNotificationChannel(channel)
        }
    }

    private fun buildNotification(): Notification {
        val intent = Intent(this, MainActivity::class.java)
        val pendingIntent = PendingIntent.getActivity(
            this,
            0,
            intent,
            PendingIntent.FLAG_IMMUTABLE
        )
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle(getString(R.string.app_name))
            .setContentText(getString(R.string.mdm_service_running))
            .setSmallIcon(R.mipmap.ic_launcher)
            .setContentIntent(pendingIntent)
            .setOngoing(true)
            .build()
    }

    private fun setupService() {
        // Inicializa el DevicePolicyManager y WorkManager
        devicePolicyManager = getSystemService(Context.DEVICE_POLICY_SERVICE) as DevicePolicyManager
        workManager = WorkManager.getInstance(applicationContext)

        // Inicializa el repositorio
        val prefs = getSharedPreferences("mdm_prefs", Context.MODE_PRIVATE)
        val baseUrl = prefs.getString("server_url", BuildConfig.MDM_SERVER_URL)!!
        val apiService = ApiServiceFactory.create(baseUrl)
        val database = LogDatabase.getDatabase(applicationContext)
        repository = DeviceRepository(apiService, database.deviceDao())

        // Llamada asincrónica para registrar el dispositivo
        job = CoroutineScope(Dispatchers.IO).launch {
            try {
                repository.registerDevice(applicationContext)
                Log.d("MDMService", "Dispositivo registrado correctamente")
                startMonitoring() // Iniciar monitoreo periódicamente
            } catch (e: Exception) {
                Log.e("MDMService", "Error al registrar el dispositivo: ${e.message}")
            }
        }
    }

    // Inicia el monitoreo periódico
    private fun startMonitoring() {
        val workRequest = PeriodicWorkRequestBuilder<SyncWorker>(15, TimeUnit.MINUTES)
            .build()
        workManager.enqueue(workRequest)
        Log.d("MDMService", "Sincronización periódica programada cada 15 minutos.")
    }

    // Control del ciclo de vida del servicio
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        return START_STICKY
    }

    override fun onDestroy() {
        super.onDestroy()
        job?.cancel() // Cancelar la corutina si el servicio se destruye
    }

    override fun onBind(intent: Intent): IBinder? = null
}
