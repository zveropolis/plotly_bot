#!/bin/zsh
#Создание переменной первого аргумента
first="$1"
privkey="Nothing in privkey"
pubkey="Nothing in pubkey"

#Проверка написанного первого аргумента
if [ -n "$1" ]; then

    #Генерация ключей
    wg genkey | tee temppriv | wg pubkey >temppub
    privkey=$(cat temppriv)
    rm temppriv
    pubkey=$(cat temppub)
    rm temppub

    #Создание переменной-счётчика ip-адресов
    countpeers=$(cat TotalCountPeers)
    let countpeers++
    #Обновление счётчика IP-адресов
    echo $countpeers >TotalCountPeers

    #Добавление конфигурации сервера

    sudo echo "[Peer]" >>/etc/wireguard/wg0.conf
    sudo echo "PublicKey = "$pubkey"" >>/etc/wireguard/wg0.conf
    sudo echo "AllowedIPs = 10.0.0."$countpeers"/32" >>/etc/wireguard/wg0.conf

    #Создание конфигурации клиента

    echo "[Interface]" >"$first".conf
    echo "PrivateKey = "$privkey"" >>"$first".conf
    echo "Address = 10.0.0."$countpeers"/32" >>"$first".conf
    echo "DNS = 9.9.9.9" >>"$first".conf
    echo "" >>"$first".conf
    echo "[Peer]" >>"$first".conf
    echo "PublicKey = 1n+qbDhifMUlHX1+nT4qtcaC6ESbBX8m2JDfsaqRTn0=" >>"$first".conf
    echo "AllowedIPs = 0.0.0.0/0" >>"$first".conf
    echo "Endpoint = 185.242.107.63:51820" >>"$first".conf
    echo "10.0.0."$countpeers" - "$first"" >>IpAddressTable.txt
    sudo systemctl reload wg-quick@wg0.service
#Если нет первого аргумента
else
    echo "No parameters found. "
fi
