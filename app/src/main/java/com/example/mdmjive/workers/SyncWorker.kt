package com.example.mdmjive.workers

import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import android.util.Log
import com.example.mdmjive.network.ApiService
import com.example.mdmjive.database.DeviceDao
import com.example.mdmjive.repository.DeviceRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

class SyncWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    private val TAG = "SyncWorker"
    private val deviceRepository: DeviceRepository = DeviceRepository(ApiService.create(), DeviceDao())

    override suspend fun doWork(): Result {
        return try {
            // Sincronizar con el servidor
            Log.d(TAG, "Iniciando la sincronización del dispositivo...")

            // Llamada al repositorio para sincronizar
            deviceRepository.syncWithServer()

            Log.d(TAG, "Sincronización completada con éxito")
            Result.success()
        } catch (e: Exception) {
            Log.e(TAG, "Error durante la sincronización: ${e.message}")
            Result.retry() // Intentar de nuevo en caso de error
        }
    }
}
