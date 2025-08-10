package com.example.mdmjive.services

import com.google.firebase.messaging.FirebaseMessagingService
import com.google.firebase.messaging.RemoteMessage
import android.util.Log
import com.example.mdmjive.controls.CommandExecutor
import com.example.mdmjive.network.models.Command
import com.example.mdmjive.utils.TokenManager
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

class FCMService : FirebaseMessagingService() {
    override fun onNewToken(token: String) {
        super.onNewToken(token)
        Log.d("FCMService", "Nuevo token: $token")
        TokenManager.saveToken(applicationContext, token)
    }

    override fun onMessageReceived(message: RemoteMessage) {
        super.onMessageReceived(message)
        CoroutineScope(Dispatchers.IO).launch {
            val action = message.data["action"]
            if (action != null) {
                val command = Command(
                    action = action,
                    packageName = message.data["packageName"],
                    message = message.data["message"]
                )
                CommandExecutor(applicationContext).execute(listOf(command))
            } else {
                Log.e("FCMService", "Acción no proporcionada en el mensaje FCM")
            }
        }
    }
}
