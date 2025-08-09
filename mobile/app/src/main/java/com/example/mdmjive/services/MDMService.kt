package com.example.mdmjive.services

import android.app.Service
import android.content.Context
import android.content.Intent
import android.os.IBinder
import android.util.Log
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import com.example.mdmjive.repository.DeviceRepository
import com.example.mdmjive.network.ApiServiceFactory
import com.example.mdmjive.database.LogDatabase
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import java.util.concurrent.TimeUnit
import android.app.admin.DevicePolicyManager

class MDMService : Service() {

    private lateinit var devicePolicyManager: DevicePolicyManager
    private lateinit var repository: DeviceRepository
    private lateinit var workManager: WorkManager
    private var job: Job? = null

    override fun onCreate() {
        super.onCreate()
        setupService()
    }

    private fun setupService() {
        // Inicializa el DevicePolicyManager y WorkManager
        devicePolicyManager = getSystemService(Context.DEVICE_POLICY_SERVICE) as DevicePolicyManager
        workManager = WorkManager.getInstance(applicationContext)

        // Inicializa el repositorio
        val apiService = ApiServiceFactory.create("https://example.com/")
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
