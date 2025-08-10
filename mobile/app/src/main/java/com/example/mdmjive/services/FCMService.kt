package com.example.mdmjive.services

import com.google.firebase.messaging.FirebaseMessagingService
import com.google.firebase.messaging.RemoteMessage
import android.util.Log
import com.example.mdmjive.BuildConfig
import com.example.mdmjive.repository.DeviceRepository
import com.example.mdmjive.network.ApiServiceFactory
import com.example.mdmjive.database.LogDatabase
import com.example.mdmjive.controls.CommandExecutor
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

class FCMService : FirebaseMessagingService() {
    override fun onNewToken(token: String) {
        super.onNewToken(token)
        Log.d("FCMService", "Nuevo token: $token")
    }

    override fun onMessageReceived(message: RemoteMessage) {
        super.onMessageReceived(message)
        CoroutineScope(Dispatchers.IO).launch {
            val repository = DeviceRepository(
                ApiServiceFactory.create(BuildConfig.BASE_URL),
                LogDatabase.getDatabase(applicationContext).deviceDao()
            )
            val commands = repository.fetchCommands(applicationContext)
            if (commands.isNotEmpty()) {
                CommandExecutor(applicationContext).execute(commands)
            }
        }
    }
}
