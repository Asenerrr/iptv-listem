# -*- coding: utf-8 -*-
"""
ÖZEL SPOR, ŞAMPİYONLAR LİGİ & UFC ODAKLI TÜRKÇE IPTV BOTU
==========================================================
1. Türksat TKGS resmi kumanda sıralaması (tvg-chno: 1..19).
2. Dünyadaki tüm canlı maç, Şampiyonlar Ligi ve UFC / Dövüş kanalları:
   - TRT Spor, A Spor, TV8.5, FB TV, Sports TV, TJK TV
   - CBC Sport & İdman TV (Azerbaycan maç/UFC kanalları)
   - Arena Sport, Arena Fight, FightBox, Fight Network (UFC & Boks)
   - ZDF, RTL, ServusTV, ORF Sport, Canale 5, 1TV Georgia
   - Dünya çapında yüzlerce spor ve canlı maç kanalı.
3. %100 Türkçe Belgeseller: TRT Belgesel, DMAX, TLC, Yaban TV, TRT 2, TGRT Belgesel, Diyanet TV + Global Belgeseller.
4. Azerbaycan genel kanalları kaldırıldı, sadece CBC Sport ve İdman TV korundu.
5. Dev Sinema ve Popüler Dizi Arşivi.
6. Canlı EPG (Yayın Akışı) ve TMDB Afişleri.
"""

import os
import sys
import json
import re
import base64
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

CONFIG_FILE = "config.json"
DEFAULT_OUTPUT_FILE = "guncel_kaliteli_liste.m3u"

EPG_URLS = "https://epgshare01.online/epgshare01/epg_ripper_TR1.xml.gz,https://epgshare01.online/epgshare01/epg_ripper_ALL_SOURCES1.xml.gz"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# --- TKGS RESMI KUMANDA SIRALAMASI & EPG TANIMLARI ---
TKGS_ONCELIKLI_KANALLAR = [
    # 1. TKGS - ULUSAL KANALLAR (1..19)
    {"regex": r"\bTRT\s*1\b", "ad": "TRT 1 HD", "epg_id": "TRT.1.HD.tr", "kategori": "1. TKGS - Ulusal Kanallar", "chno": 1, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/85/TRT_1_logo_%282021-%29.svg/960px-TRT_1_logo_%282021-%29.svg.png"},
    {"regex": r"\bATV\b(?!.*(?:Avrupa|Alanya))", "ad": "ATV HD", "epg_id": "ATV.HD.tr", "kategori": "1. TKGS - Ulusal Kanallar", "chno": 2, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e6/Atv_logo.svg/800px-Atv_logo.svg.png"},
    {"regex": r"\bKanal\s*D\b", "ad": "KANAL D HD", "epg_id": "KANAL.D.HD.tr", "kategori": "1. TKGS - Ulusal Kanallar", "chno": 3, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cf/Kanal_D_logo.svg/800px-Kanal_D_logo.svg.png"},
    {"regex": r"\bShow\s*TV\b|\bShow\s*Turk\b", "ad": "SHOW TV HD", "epg_id": "SHOW.TV.HD.tr", "kategori": "1. TKGS - Ulusal Kanallar", "chno": 4, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Show_TV_logo_%282021%29.svg/800px-Show_TV_logo_%282021%29.svg.png"},
    {"regex": r"\bStar\s*TV\b", "ad": "STAR TV HD", "epg_id": "STAR.TV.HD.tr", "kategori": "1. TKGS - Ulusal Kanallar", "chno": 5, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Star_TV_logo.svg/800px-Star_TV_logo.svg.png"},
    {"regex": r"\bTV\s*8\b(?!.*5)", "ad": "TV8 HD", "epg_id": "TV8.HD.tr", "kategori": "1. TKGS - Ulusal Kanallar", "chno": 6, "logo": "https://upload.wikimedia.org/wikipedia/tr/thumb/6/68/Tv8_Yeni_Logo.png/960px-Tv8_Yeni_Logo.png"},
    {"regex": r"\bNOW\b|\bFOX\b(?!.*(?:Sport|Life|Crime))", "ad": "NOW TV HD", "epg_id": "FOX.HD.tr", "kategori": "1. TKGS - Ulusal Kanallar", "chno": 7, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Now_T%C3%BCrkiye_Logo.png/800px-Now_T%C3%BCrkiye_Logo.png"},
    {"regex": r"\bKanal\s*7\b", "ad": "KANAL 7 HD", "epg_id": "KANAL.7.HD.tr", "kategori": "1. TKGS - Ulusal Kanallar", "chno": 8, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/Kanal_7_logo.svg/800px-Kanal_7_logo.svg.png"},
    {"regex": r"\bBeyaz\s*TV\b", "ad": "BEYAZ TV HD", "epg_id": "BEYAZ.TV.HD.tr", "kategori": "1. TKGS - Ulusal Kanallar", "chno": 9, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/Beyaz_TV_logo.svg/800px-Beyaz_TV_logo.svg.png"},
    {"regex": r"\bA2\s*TV\b|\bA2\b", "ad": "A2 HD", "epg_id": "A2.HD.tr", "kategori": "1. TKGS - Ulusal Kanallar", "chno": 10, "logo": "https://iatv.tmgrup.com.tr/site/v2/a2tv/i/a2tv-logo.png"},
    {"regex": r"\bTeve\s*2\b|\bTV\s*2\b", "ad": "TEVE2 HD", "epg_id": "TEVE2.HD.tr", "kategori": "1. TKGS - Ulusal Kanallar", "chno": 11, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Teve2_logo.png/800px-Teve2_logo.png"},
    {"regex": r"\bTLC\b", "ad": "TLC HD (Türkçe)", "epg_id": "TLC.HD.tr", "kategori": "1. TKGS - Ulusal Kanallar", "chno": 12, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/TLC_Logo_2016.svg/800px-TLC_Logo_2016.svg.png"},
    {"regex": r"\bDMAX\b", "ad": "DMAX HD (Türkçe)", "epg_id": "DMAX.HD.tr", "kategori": "1. TKGS - Ulusal Kanallar", "chno": 13, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/DMAX_Logo.svg/800px-DMAX_Logo.svg.png"},
    {"regex": r"\b360\s*TV\b|\b360\b", "ad": "360 TV HD", "epg_id": "360.HD.tr", "kategori": "1. TKGS - Ulusal Kanallar", "chno": 14, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/29/360_TV_Logo.png/800px-360_TV_Logo.png"},
    {"regex": r"\bTV\s*4\b", "ad": "TV4 HD", "epg_id": "TVT.tr", "kategori": "1. TKGS - Ulusal Kanallar", "chno": 15, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/TV4_logo.png/800px-TV4_logo.png"},
    {"regex": r"\bTRT\s*4K\b", "ad": "TRT 4K ULTRA HD", "epg_id": "TRT.1.HD.tr", "kategori": "1. TKGS - Ulusal Kanallar", "chno": 16, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/TRT_4K_logo_%282021-%29.svg/800px-TRT_4K_logo_%282021-%29.svg.png"},
    {"regex": r"\bATV\s*Avrupa\b", "ad": "ATV AVRUPA", "epg_id": "ATV.tr", "kategori": "1. TKGS - Ulusal Kanallar", "chno": 17, "logo": "https://i.tmgrup.com.tr/aav/site/v1/i/atv-avrupa-logo.png"},
    {"regex": r"\bEuro\s*D\b", "ad": "EURO D", "epg_id": "KANAL.D.tr", "kategori": "1. TKGS - Ulusal Kanallar", "chno": 18, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cf/Kanal_D_logo.svg/800px-Kanal_D_logo.svg.png"},
    {"regex": r"\bEuro\s*Star\b", "ad": "EURO STAR", "epg_id": "STAR.TV.tr", "kategori": "1. TKGS - Ulusal Kanallar", "chno": 19, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/38/Star_TV_logo.svg/800px-Star_TV_logo.svg.png"},

    # 2. TKGS - HABER KANALLARI (20..39)
    {"regex": r"\bTRT\s*Haber\b", "ad": "TRT HABER HD", "epg_id": "TRT.HABER.HD.tr", "kategori": "2. TKGS - Haber Kanalları", "chno": 20, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/72/TRT_Haber_Eyl%C3%BCl_2020_Logo.svg/800px-TRT_Haber_Eyl%C3%BCl_2020_Logo.svg.png"},
    {"regex": r"\bNTV\b", "ad": "NTV HD", "epg_id": "NTV.HD.tr", "kategori": "2. TKGS - Haber Kanalları", "chno": 21, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/Ntv_logo.svg/800px-Ntv_logo.svg.png"},
    {"regex": r"\bCNN\s*T[uü]rk\b", "ad": "CNN TÜRK HD", "epg_id": "CNN.TÜRK.HD.tr", "kategori": "2. TKGS - Haber Kanalları", "chno": 22, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/CNN_T%C3%BCrk_logo.svg/800px-CNN_T%C3%BCrk_logo.svg.png"},
    {"regex": r"\bHabert[uü]rk\b", "ad": "HABERTÜRK HD", "epg_id": "HABERTÜRK.tr", "kategori": "2. TKGS - Haber Kanalları", "chno": 23, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Habert%C3%BCrk_logo.svg/800px-Habert%C3%BCrk_logo.svg.png"},
    {"regex": r"\bA\s*Haber\b", "ad": "A HABER HD", "epg_id": "A.HABER.HD.tr", "kategori": "2. TKGS - Haber Kanalları", "chno": 24, "logo": "https://upload.wikimedia.org/wikipedia/commons/7/7c/Ahaber_Logo.png"},
    {"regex": r"\bS[oö]zc[uü]\s*TV\b|\bSZC\s*TV\b", "ad": "SÖZCÜ TV (SZC) HD", "epg_id": "SZC.tr", "kategori": "2. TKGS - Haber Kanalları", "chno": 25, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cf/Szc_tv_logo.png/800px-Szc_tv_logo.png"},
    {"regex": r"\bHalk\s*TV\b", "ad": "HALK TV HD", "epg_id": "HALK.TV.tr", "kategori": "2. TKGS - Haber Kanalları", "chno": 26, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Halk_TV_logo.svg/800px-Halk_TV_logo.svg.png"},
    {"regex": r"\bTele\s*1\b", "ad": "TELE1 HD", "epg_id": "TELE1.tr", "kategori": "2. TKGS - Haber Kanalları", "chno": 27, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Tele1_logo.png/800px-Tele1_logo.png"},
    {"regex": r"\bTV\s*100\b", "ad": "TV100 HD", "epg_id": "TV100.tr", "kategori": "2. TKGS - Haber Kanalları", "chno": 28, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Tv100_logo.png/800px-Tv100_logo.png"},
    {"regex": r"\bBloomberg\s*HT\b", "ad": "BLOOMBERG HT HD", "epg_id": "BLOOMBERG.HT.HD.tr", "kategori": "2. TKGS - Haber Kanalları", "chno": 29, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Bloomberg_HT_logo.svg/800px-Bloomberg_HT_logo.svg.png"},
    {"regex": r"\b24\s*TV\b", "ad": "24 TV HD", "epg_id": "24.TV.tr", "kategori": "2. TKGS - Haber Kanalları", "chno": 30, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e9/24_TV_Logo.png/800px-24_TV_Logo.png"},
    {"regex": r"\b[UÜ]lke\s*TV\b", "ad": "ÜLKE TV HD", "epg_id": "ÜLKE.TV.HD.tr", "kategori": "2. TKGS - Haber Kanalları", "chno": 31, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/%C3%9Clke_TV_logo.png/800px-%C3%9Clke_TV_logo.png"},
    {"regex": r"\bTGRT\s*Haber\b", "ad": "TGRT HABER HD", "epg_id": "TGRT.HABER.tr", "kategori": "2. TKGS - Haber Kanalları", "chno": 32, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/TGRT_Haber_logo.svg/800px-TGRT_Haber_logo.svg.png"},
    {"regex": r"\bTVNET\b|\bTV\s*Net\b", "ad": "TVNET HD", "epg_id": "TVNET.HD.tr", "kategori": "2. TKGS - Haber Kanalları", "chno": 33, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/TVNET_logo.png/800px-TVNET_logo.png"},
    {"regex": r"\bBeng[uü]t[uü]rk\b", "ad": "BENGÜTÜRK TV HD", "epg_id": "BENGÜ.TÜRK.tr", "kategori": "2. TKGS - Haber Kanalları", "chno": 34, "logo": "https://i.imgur.com/p3ON1oX.png"},
    {"regex": r"\bTRT\s*World\b", "ad": "TRT WORLD HD", "epg_id": "TRT.WORLD.HD.tr", "kategori": "2. TKGS - Haber Kanalları", "chno": 35, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/92/TRT_World_logo.svg/800px-TRT_World_logo.svg.png"},

    # 3. SPOR & CANLI MAÇ & UFC KANALLARI (40..59)
    {"regex": r"\bTRT\s*Spor\b(?!.*Y[ıi]ld[ıi]z)", "ad": "TRT SPOR HD (Şampiyonlar Ligi)", "epg_id": "TRT.SPOR.HD.tr", "kategori": "3. TKGS - Spor & Canlı Maç / UFC", "chno": 40, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/TRT_Spor_logo_%282021-%29.svg/800px-TRT_Spor_logo_%282021-%29.svg.png"},
    {"regex": r"\bTRT\s*Spor\s*Y[ıi]ld[ıi]z\b", "ad": "TRT SPOR YILDIZ HD", "epg_id": "TRT.SPOR.HD.tr", "kategori": "3. TKGS - Spor & Canlı Maç / UFC", "chno": 41, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/ce/TRT_Spor_Y%C4%B1ld%C4%B1z_Logo.svg/800px-TRT_Spor_Y%C4%B1ld%C4%B1z_Logo.svg.png"},
    {"regex": r"\bA\s*Spor\b", "ad": "A SPOR HD", "epg_id": "A.SPOR.tr", "kategori": "3. TKGS - Spor & Canlı Maç / UFC", "chno": 42, "logo": "https://i.imgur.com/ZhkZzLf.png"},
    {"regex": r"\bTV\s*8\.5\b|\bTV\s*8,5\b", "ad": "TV8.5 HD (Şampiyonlar Ligi Maçları)", "epg_id": "TV8.HD.tr", "kategori": "3. TKGS - Spor & Canlı Maç / UFC", "chno": 43, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/TV8_5_Logo.png/800px-TV8_5_Logo.png"},
    {"regex": r"\bCBC\s*Sport\b", "ad": "CBC SPORT HD (Şampiyonlar Ligi & Premier Ligi)", "epg_id": "CBCSport.az", "kategori": "3. TKGS - Spor & Canlı Maç / UFC", "chno": 44, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/CBC_Sport_logo.png/800px-CBC_Sport_logo.png"},
    {"regex": r"\b[Iİi]dman\b|\bIdman\s*TV\b", "ad": "İDMAN TV HD (Şampiyonlar Ligi & UFC)", "epg_id": "IdmanTV.az", "kategori": "3. TKGS - Spor & Canlı Maç / UFC", "chno": 45, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Idman_TV_logo.png/800px-Idman_TV_logo.png"},
    {"regex": r"\bFB\s*TV\b|\bFenerbah[cç]e\s*TV\b", "ad": "FB TV HD", "epg_id": "FENERBAHÇE.TV.tr", "kategori": "3. TKGS - Spor & Canlı Maç / UFC", "chno": 46, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6f/Fenerbah%C3%A7e_TV_logo.png/800px-Fenerbah%C3%A7e_TV_logo.png"},
    {"regex": r"\bSports\s*TV\b", "ad": "SPORTS TV HD", "epg_id": "SPORTS.TV.tr", "kategori": "3. TKGS - Spor & Canlı Maç / UFC", "chno": 47, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/18/Sports_TV_logo.png/800px-Sports_TV_logo.png"},
    {"regex": r"\bTJK\s*TV\b", "ad": "TJK TV HD", "epg_id": "TJK.tr", "kategori": "3. TKGS - Spor & Canlı Maç / UFC", "chno": 48, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/TJK_TV_logo.png/800px-TJK_TV_logo.png"},
    {"regex": r"\bZDF\b", "ad": "ZDF HD (Almanya - Şampiyonlar Ligi)", "epg_id": "ZDF.de", "kategori": "3. TKGS - Spor & Canlı Maç / UFC", "chno": 49, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/64/ZDF_logo.svg/800px-ZDF_logo.svg.png"},
    {"regex": r"\bRTL\b(?!.*(?:2|II|Crime|Living))", "ad": "RTL HD (Almanya - Avrupa Ligi)", "epg_id": "RTL.de", "kategori": "3. TKGS - Spor & Canlı Maç / UFC", "chno": 50, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f4/RTL_logo_2021.svg/800px-RTL_logo_2021.svg.png"},
    {"regex": r"\bServus\s*TV\b|\bServusTV\b", "ad": "SERVUSTV HD (Avusturya - Şampiyonlar Ligi)", "epg_id": "ServusTV.at", "kategori": "3. TKGS - Spor & Canlı Maç / UFC", "chno": 51, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/82/ServusTV_logo.svg/800px-ServusTV_logo.svg.png"},
    {"regex": r"\bORF\s*1\b|\bORF\s*Sport\b", "ad": "ORF SPORT HD (Avusturya)", "epg_id": "ORFSportPlus.at", "kategori": "3. TKGS - Spor & Canlı Maç / UFC", "chno": 52, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/ORF_1_logo.svg/800px-ORF_1_logo.svg.png"},

    # 4. GERÇEK TÜRKÇE BELGESEL KANALLARI (60..79)
    {"regex": r"\bTRT\s*Belgesel\b", "ad": "TRT BELGESEL HD (Orijinal Türkçe)", "epg_id": "TRT.BELGESEL.HD.tr", "kategori": "4. Belgesel Dünyası (Türkçe)", "chno": 60, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/TRT_Belgesel_logo_%282019-%29.svg/800px-TRT_Belgesel_logo_%282019-%29.svg.png"},
    {"regex": r"\bYaban\s*TV\b", "ad": "YABAN TV HD (Doğa & Vahşi Yaşam)", "epg_id": "YabanTV.tr", "kategori": "4. Belgesel Dünyası (Türkçe)", "chno": 61, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Yaban_TV_logo.png/800px-Yaban_TV_logo.png"},
    {"regex": r"\bTRT\s*2\b", "ad": "TRT 2 KÜLTÜR & TARİH BELGESEL HD", "epg_id": "TRT.2.tr", "kategori": "4. Belgesel Dünyası (Türkçe)", "chno": 62, "logo": "https://i.imgur.com/iOCQdyD.png"},
    {"regex": r"\bDiyanet\s*TV\b", "ad": "DİYANET TV HD (Tarih & Medeniyet)", "epg_id": "DiyanetTV.tr", "kategori": "4. Belgesel Dünyası (Türkçe)", "chno": 63, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Diyanet_TV_logo.png/800px-Diyanet_TV_logo.png"},
    {"regex": r"\bTRT\s*T[uü]rk\b", "ad": "TRT TÜRK HD (Kültür & Coğrafya)", "epg_id": "TRT.TÜRK.tr", "kategori": "4. Belgesel Dünyası (Türkçe)", "chno": 64, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d2/TRT_T%C3%BCrk_logo.svg/800px-TRT_T%C3%BCrk_logo.svg.png"},
    {"regex": r"\bTRT\s*Avaz\b", "ad": "TRT AVAZ HD (Kültür & Doğa)", "epg_id": "TRT.AVAZ.HD.tr", "kategori": "4. Belgesel Dünyası (Türkçe)", "chno": 65, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/TRT_Avaz_logo.svg/800px-TRT_Avaz_logo.svg.png"},
    {"regex": r"\bLove\s*Nature\b", "ad": "LOVE NATURE 4K (Vahşi Doğa)", "epg_id": "LoveNature.tr", "kategori": "4. Belgesel Dünyası (Türkçe)", "chno": 66, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Love_Nature_logo.png/800px-Love_Nature_logo.png"},
    {"regex": r"\bNational\s*Geographic\b|\bNat\s*Geo\b(?!.*Wild)", "ad": "NATIONAL GEOGRAPHIC HD", "epg_id": "NATIONAL.GEOGRAPHIC.HD.tr", "kategori": "4. Belgesel Dünyası (Türkçe)", "chno": 67, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fc/Natgeologo.svg/800px-Natgeologo.svg.png"},
    {"regex": r"\bNat\s*Geo\s*Wild\b|\bNational\s*Geographic\s*Wild\b", "ad": "NAT GEO WILD HD", "epg_id": "NATIONAL.GEOGRAPHIC.WILD.tr", "kategori": "4. Belgesel Dünyası (Türkçe)", "chno": 68, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/Nat_Geo_Wild_logo.svg/800px-Nat_Geo_Wild_logo.svg.png"},
    {"regex": r"\bDiscovery\s*Channel\b|\bDiscovery\b(?!.*Science)", "ad": "DISCOVERY CHANNEL HD", "epg_id": "DiscoveryChannel.tr", "kategori": "4. Belgesel Dünyası (Türkçe)", "chno": 69, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/22/Discovery_Channel_2019.svg/800px-Discovery_Channel_2019.svg.png"},
    {"regex": r"\bDiscovery\s*Science\b|\bScience\s*Channel\b", "ad": "DISCOVERY SCIENCE HD", "epg_id": "DISCOVERY.SCIENCE.HD.tr", "kategori": "4. Belgesel Dünyası (Türkçe)", "chno": 70, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Science_Channel_logo.svg/800px-Science_Channel_logo.svg.png"},
    {"regex": r"\bBBC\s*Earth\b", "ad": "BBC EARTH HD", "epg_id": "BBCEarth.tr", "kategori": "4. Belgesel Dünyası (Türkçe)", "chno": 71, "logo": "https://i.imgur.com/nGSsUd4.png"},
    {"regex": r"\bHistory\s*Channel\b|\bHistory\b(?!.*2)", "ad": "HISTORY CHANNEL HD", "epg_id": "HistoryChannel.tr", "kategori": "4. Belgesel Dünyası (Türkçe)", "chno": 72, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/01/History_%282021%29.svg/800px-History_%282021%29.svg.png"},
    {"regex": r"\bHistory\s*2\b|\bH2\b", "ad": "HISTORY 2 (H2) HD", "epg_id": "History2.tr", "kategori": "4. Belgesel Dünyası (Türkçe)", "chno": 73, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/History2_logo_%282022%29.svg/800px-History2_logo_%282022%29.svg.png"},
    {"regex": r"\bAnimal\s*Planet\b", "ad": "ANIMAL PLANET HD", "epg_id": "ANIMAL.PLANET.HD.tr", "kategori": "4. Belgesel Dünyası (Türkçe)", "chno": 74, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/Animal_Planet_2018.svg/800px-Animal_Planet_2018.svg.png"},
    {"regex": r"\bViasat\s*Nature\b", "ad": "VIASAT NATURE HD", "epg_id": "VIASAT.NATURE.-.HISTORY.tr", "kategori": "4. Belgesel Dünyası (Türkçe)", "chno": 75, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/02/Viasat_Nature_logo.svg/800px-Viasat_Nature_logo.svg.png"},
    {"regex": r"\bViasat\s*History\b", "ad": "VIASAT HISTORY HD", "epg_id": "VIASAT.NATURE.-.HISTORY.tr", "kategori": "4. Belgesel Dünyası (Türkçe)", "chno": 76, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f6/Viasat_History_logo.svg/800px-Viasat_History_logo.svg.png"},
    {"regex": r"\bViasat\s*Explore\b", "ad": "VIASAT EXPLORE HD", "epg_id": "VIASAT.EXPLORE.tr", "kategori": "4. Belgesel Dünyası (Türkçe)", "chno": 77, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a1/Viasat_Explore_logo.svg/800px-Viasat_Explore_logo.svg.png"},

    # 5. TKGS - ÇOCUK & ÇİZGİ FİLM (80..89)
    {"regex": r"\bTRT\s*[CÇ]ocuk\b", "ad": "TRT ÇOCUK HD", "epg_id": "TRT.ÇOCUK.tr", "kategori": "5. TKGS - Çocuk & Çizgi Film", "chno": 80, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/TRT_%C3%87ocuk_logo_%282021%29.svg/800px-TRT_%C3%87ocuk_logo_%282021%29.svg.png"},
    {"regex": r"\bMinika\s*[CÇ]ocuk\b", "ad": "MİNİKA ÇOCUK HD", "epg_id": "MİNİKA.ÇOCUK.tr", "kategori": "5. TKGS - Çocuk & Çizgi Film", "chno": 81, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2b/Minika_%C3%87ocuk_logo.png/800px-Minika_%C3%87ocuk_logo.png"},
    {"regex": r"\bMinika\s*GO\b", "ad": "MİNİKA GO HD", "epg_id": "MİNİKA.GO.tr", "kategori": "5. TKGS - Çocuk & Çizgi Film", "chno": 82, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Minika_GO_logo.png/800px-Minika_GO_logo.png"},
    {"regex": r"\bCartoon\s*Network\b", "ad": "CARTOON NETWORK HD", "epg_id": "CARTOON.NETWORK.tr", "kategori": "5. TKGS - Çocuk & Çizgi Film", "chno": 83, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/80/Cartoon_Network_2010_logo.svg/800px-Cartoon_Network_2010_logo.svg.png"},
    {"regex": r"\bBabyTV\b|\bBaby\s*TV\b", "ad": "BABY TV", "epg_id": "BABY.TV.tr", "kategori": "5. TKGS - Çocuk & Çizgi Film", "chno": 84, "logo": "https://i.imgur.com/4BDJ5FT.png"},
    {"regex": r"\bDiyanet\s*[CÇ]ocuk\b", "ad": "DİYANET ÇOCUK HD", "epg_id": "TRT.ÇOCUK.tr", "kategori": "5. TKGS - Çocuk & Çizgi Film", "chno": 85, "logo": "https://i.imgur.com/8PmXz9t.png"},

    # 6. TKGS - MÜZİK KANALLARI (90..99)
    {"regex": r"\bTRT\s*M[uü]zik\b", "ad": "TRT MÜZİK HD", "epg_id": "TRT.MÜZİK.tr", "kategori": "6. TKGS - Müzik Kanalları", "chno": 90, "logo": "https://i.imgur.com/JgUzRH8.png"},
    {"regex": r"\bPower\s*T[uü]rk\b", "ad": "POWER TÜRK HD", "epg_id": "POWER.TV.HD.tr", "kategori": "6. TKGS - Müzik Kanalları", "chno": 91, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/PowerT%C3%BCrk_TV_logo.png/800px-PowerT%C3%BCrk_TV_logo.png"},
    {"regex": r"\bPower\s*TV\b", "ad": "POWER TV HD", "epg_id": "POWER.TV.HD.tr", "kategori": "6. TKGS - Müzik Kanalları", "chno": 92, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/Power_TV_logo.png/800px-Power_TV_logo.png"},
    {"regex": r"\bKral\s*Pop\b", "ad": "KRAL POP TV HD", "epg_id": "KralPop.tr", "kategori": "6. TKGS - Müzik Kanalları", "chno": 93, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Kral_Pop_TV_logo.png/800px-Kral_Pop_TV_logo.png"},
    {"regex": r"\bKral\s*TV\b", "ad": "KRAL TV", "epg_id": "KralTV.tr", "kategori": "6. TKGS - Müzik Kanalları", "chno": 94, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/Kral_TV_logo.png/800px-Kral_TV_logo.png"},
    {"regex": r"\bNumber\s*1\s*T[uü]rk\b", "ad": "NUMBER 1 TÜRK HD", "epg_id": "NumberOneTurk.tr", "kategori": "6. TKGS - Müzik Kanalları", "chno": 95, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/46/Number_1_T%C3%BCrk_logo.png/800px-Number_1_T%C3%BCrk_logo.png"},
    {"regex": r"\bNumber\s*1\b", "ad": "NUMBER 1 TV HD", "epg_id": "NumberOne.tr", "kategori": "6. TKGS - Müzik Kanalları", "chno": 96, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7a/Number_1_TV_logo.png/800px-Number_1_TV_logo.png"},
    {"regex": r"\bDream\s*T[uü]rk\b", "ad": "DREAM TÜRK HD", "epg_id": "DREAM.TV.tr", "kategori": "6. TKGS - Müzik Kanalları", "chno": 97, "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Dream_T%C3%BCrk_logo.png/800px-Dream_T%C3%BCrk_logo.png"},
]

# Generic Azerbaijani channels to exclude (AzTV, Space, Medeniyyet)
AZERBAYCAN_GENEL_KANALLAR = ["aztv", "space tv", "medeniyyet", "məvəniyyət", "ictimai", "arb", "xazar"]


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    return {}


def parse_m3u(icerik):
    kanallar = []
    lines = icerik.splitlines()
    i = 0
    current_title = ""
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("#EXTINF:"):
            extinf = line
            url = ""
            i += 1
            while i < len(lines) and (not lines[i].strip() or lines[i].strip().startswith("#")):
                i += 1
            if i < len(lines):
                url = lines[i].strip()
                if url.startswith("http://") or url.startswith("https://"):
                    match_name = extinf.split(",")[-1].strip() if "," in extinf else ""
                    if "Program (" in match_name or re.search(r"index-\d+-\d+\.m3u8", url):
                        i += 1
                        continue
                    
                    # Exclude general Azerbaijani non-sports channels
                    if any(az in match_name.lower() for az in AZERBAYCAN_GENEL_KANALLAR):
                        i += 1
                        continue
                    
                    logo_match = re.search(r'tvg-logo="([^"]+)"', extinf)
                    logo = logo_match.group(1) if logo_match else ""
                    grp_match = re.search(r'group-title="([^"]+)"', extinf)
                    grp = grp_match.group(1) if grp_match else ""
                    
                    kanallar.append({
                        "extinf": extinf,
                        "url": url,
                        "raw_name": match_name,
                        "logo": logo,
                        "raw_group": grp
                    })
        elif line.startswith("-") and line.endswith("-"):
            current_title = line.strip("- \t").replace("M3U8", "").replace("HD", "").strip()
        elif line.startswith("http://") or line.startswith("https://"):
            name = current_title if current_title else "Canlı Yayın"
            if not any(az in name.lower() for az in AZERBAYCAN_GENEL_KANALLAR):
                kanallar.append({
                    "extinf": f'#EXTINF:-1 group-title="9. Türkiye Yerel & Şehir Kanalları",{name}',
                    "url": line,
                    "raw_name": name,
                    "logo": "",
                    "raw_group": "Yerel"
                })
            current_title = ""
        i += 1
    return kanallar


def tkgs_eslestir(raw_name):
    for item in TKGS_ONCELIKLI_KANALLAR:
        if re.search(item["regex"], raw_name, re.IGNORECASE):
            return item
    return None


def akilli_kategori_ata(kanal):
    raw_name = kanal["raw_name"].lower()
    raw_group = kanal.get("raw_group", "").lower()

    # 1. Spor, Canlı Maç, UFC, Dövüş Kanalları
    if any(term in raw_name or term in raw_group for term in ["spor", "sport", "fight", "ufc", "box", "boks", "match", "futbol", "football", "basket", "racing", "tjk", "arena", "sky", "dazn", "espn", "bein", "polsat", "super", "tnt", "cbc", "idman"]):
        return "3. TKGS - Spor & Canlı Maç / UFC"

    # 2. Popüler Dizi & Sezon Arşivi
    if any(term in raw_name or term in raw_group for term in ["dizi", "series", "sezon", "bölüm", "s01", "s02", "s03", "s04", "s05", "e01", "e02", "e03", "e04", "ep"]):
        return "8. Popüler Diziler & Arşiv"

    # 3. Sinema & Film Kanalları
    if any(term in raw_name or term in raw_group for term in ["film", "sinema", "cinema", "movie", "box office", "yeşilçam", "yerli film", "yabancı film", "aksiyon", "komedi", "korku", "dram", "bilim kurgu", "animasyon"]):
        return "7. Sinema & 7/24 Filmler"

    # 4. Belgesel
    if any(term in raw_name or term in raw_group for term in ["belgesel", "documentary", "nature", "wild", "planet", "history", "geograph", "explore", "science", "yaban"]):
        return "4. Belgesel Dünyası (Türkçe)"

    # 5. Çocuk
    if any(term in raw_name or term in raw_group for term in ["çocuk", "cocuk", "kids", "cartoon", "baby", "disney"]):
        return "5. TKGS - Çocuk & Çizgi Film"

    # 6. Müzik
    if any(term in raw_name or term in raw_group for term in ["müzik", "muzik", "music", "kral", "power", "number 1", "dream"]):
        return "6. TKGS - Müzik Kanalları"

    # 7. Haber
    if any(term in raw_name or term in raw_group for term in ["haber", "news", "gazete"]):
        return "2. TKGS - Haber Kanalları"

    # 8. Yerel & Şehir Kanalları
    if any(term in raw_name or term in raw_group for term in ["tv", "kanal", "ege", "akdeniz", "karadeniz", "bursa", "izmir", "antalya", "konya", "kayseri", "urfa", "trabzon", "samsun", "ordu", "adana", "gaziantep"]):
        return "9. Türkiye Yerel & Şehir Kanalları"

    return "10. Dünya Spor & Eğlence Kanalları"


def stream_test_et(kanal, timeout=2.5):
    url = kanal["url"]
    try:
        res = requests.get(url, headers=HEADERS, timeout=timeout, stream=True, allow_redirects=True, verify=False)
        if res.status_code in (200, 206, 302, 301):
            res.close()
            return kanal
        res.close()
    except Exception:
        pass
    return None


def kanallari_tara_sirala_ve_filtrele(config):
    kaynaklar = config.get("kaynak_listeler", [])
    threads = config.get("ayarlar", {}).get("kontrol_thread_sayisi", 60)
    timeout = config.get("ayarlar", {}).get("timeout_saniye", 2.5)

    tum_kanallar = []
    print(f"\n[1/3] Kaynak listeler taranıyor ({len(kaynaklar)} kaynak)...")

    for k in kaynaklar:
        ad = k.get("ad", "Bilinmeyen")
        url = k.get("url")
        try:
            print(f"  -> İndiriliyor: {ad}")
            r = requests.get(url, headers=HEADERS, timeout=15, verify=False)
            if r.status_code == 200:
                parsed = parse_m3u(r.text)
                print(f"     Bulunan ham içerik sayısı: {len(parsed)}")
                tum_kanallar.extend(parsed)
        except Exception as e:
            print(f"     [!] {ad} indirilirken hata: {e}")

    benzersiz_kanallar = []
    gorulen_urller = set()
    for k in tum_kanallar:
        if k["url"] not in gorulen_urller:
            gorulen_urller.add(k["url"])
            benzersiz_kanallar.append(k)

    tkgs_adaylari = []
    kategori_havuzlari = {
        "3. TKGS - Spor & Canlı Maç / UFC": [],
        "7. Sinema & 7/24 Filmler": [],
        "8. Popüler Diziler & Arşiv": [],
        "4. Belgesel Dünyası (Türkçe)": [],
        "9. Türkiye Yerel & Şehir Kanalları": [],
        "5. TKGS - Çocuk & Çizgi Film": [],
        "6. TKGS - Müzik Kanalları": [],
        "2. TKGS - Haber Kanalları": [],
        "10. Dünya Spor & Eğlence Kanalları": []
    }

    for k in benzersiz_kanallar:
        eslesme = tkgs_eslestir(k["raw_name"])
        if eslesme:
            k_copy = dict(k)
            k_copy["duzenlenmis_ad"] = eslesme["ad"]
            k_copy["epg_id"] = eslesme.get("epg_id", "")
            k_copy["kategori"] = eslesme["kategori"]
            k_copy["chno"] = eslesme["chno"]
            if eslesme.get("logo"):
                k_copy["logo"] = eslesme["logo"]
            tkgs_adaylari.append(k_copy)
        else:
            kat = akilli_kategori_ata(k)
            k_copy = dict(k)
            k_copy["duzenlenmis_ad"] = re.sub(r"\s*\(\d+p\).*$", "", k["raw_name"]).strip()
            k_copy["epg_id"] = ""
            k_copy["kategori"] = kat
            k_copy["chno"] = 200
            if kat in kategori_havuzlari:
                kategori_havuzlari[kat].append(k_copy)

    tkgs_adaylari.sort(key=lambda x: x["chno"])

    print(f"\n[2/3] TKGS Öncelikli Kanallar test ediliyor ({len(tkgs_adaylari)} aday)...")

    calisan_tkgs = []
    eklenen_isimler = set()

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(stream_test_et, k, timeout): k for k in tkgs_adaylari}
        for future in as_completed(futures):
            res = future.result()
            if res:
                ad = res["duzenlenmis_ad"]
                if ad not in eklenen_isimler:
                    eklenen_isimler.add(ad)
                    calisan_tkgs.append(res)

    calisan_tkgs.sort(key=lambda x: x["chno"])
    print(f"  [+] Çalışan Benzersiz TKGS Kanal Sayısı: {len(calisan_tkgs)}")

    # Kategorilere göre genişletilmiş limitler (Spor, UFC, Sinema ve Dizi odaklı)
    kategori_limitleri = {
        "3. TKGS - Spor & Canlı Maç / UFC": 250,
        "7. Sinema & 7/24 Filmler": 1200,
        "8. Popüler Diziler & Arşiv": 1500,
        "4. Belgesel Dünyası (Türkçe)": 80,
        "9. Türkiye Yerel & Şehir Kanalları": 150,
        "5. TKGS - Çocuk & Çizgi Film": 80,
        "6. TKGS - Müzik Kanalları": 60,
        "10. Dünya Spor & Eğlence Kanalları": 80
    }

    calisan_diger_tum = []

    for kat, havuz in kategori_havuzlari.items():
        limit = kategori_limitleri.get(kat, 100)
        if not havuz:
            continue
        print(f"  -> Test ediliyor: {kat} ({len(havuz)} adaydan en fazla {limit} adet)...")
        kat_calisan = []
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(stream_test_et, k, timeout) for k in havuz[:limit * 2]]
            for future in as_completed(futures):
                res = future.result()
                if res:
                    ad = res["duzenlenmis_ad"]
                    if ad not in eklenen_isimler and len(ad) > 2:
                        eklenen_isimler.add(ad)
                        kat_calisan.append(res)
                        if len(kat_calisan) >= limit:
                            break
        print(f"     [+] {kat}: {len(kat_calisan)} aktif içerik eklendi.")
        calisan_diger_tum.extend(kat_calisan)

    # Sıralı kanal numarası ata
    for idx, item in enumerate(calisan_diger_tum, start=100):
        item["chno"] = idx

    final_liste = calisan_tkgs + calisan_diger_tum
    print(f"\n[+] Toplam Hazırlanan Dev Liste Sayısı: {len(final_liste)}")
    return final_liste


def m3u_dosyasi_kaydet(kanallar, dosya_yolu):
    with open(dosya_yolu, "w", encoding="utf-8") as f:
        f.write(f'#EXTM3U url-tvg="{EPG_URLS}" x-tvg-url="{EPG_URLS}" name="Turksat TKGS, Spor, Sinema & Dizi Arsivi"\n')
        for k in kanallar:
            ad = k.get("duzenlenmis_ad", k.get("raw_name", "Kanal"))
            kategori = k.get("kategori", "1. TKGS - Ulusal Kanallar")
            chno = k.get("chno", 1)
            logo = k.get("logo", "")
            epg_id = k.get("epg_id", "")
            
            logo_str = f' tvg-logo="{logo}"' if logo else ''
            epg_str = f' tvg-id="{epg_id}" tvg-name="{ad}"' if epg_id else f' tvg-name="{ad}"'
            f.write(f'#EXTINF:-1 tvg-chno="{chno}"{epg_str} group-title="{kategori}"{logo_str},{ad}\n')
            f.write(f"{k['url']}\n")
    print(f"\n[+] Canlı Maç, Spor, Sinema & TKGS M3U listesi oluşturuldu: {dosya_yolu}")


def github_api_ile_yukle(dosya_yolu, github_config):
    token = github_config.get("token", "").strip()
    kullanici = github_config.get("kullanici_adi", "").strip()
    repo = github_config.get("repo", "").strip()
    dosya_adi = github_config.get("dosya_adi", DEFAULT_OUTPUT_FILE).strip()
    branch = github_config.get("branch", "main").strip()

    if not token or not kullanici or not repo:
        print("\n[!] UYARI: config.json içinde GitHub bilgileri eksik.")
        return None

    print(f"\n[3/3] GitHub API üzerinden '{kullanici}/{repo}' deposuna yükleme başlıyor...")

    with open(dosya_yolu, "rb") as f:
        icerik_bytes = f.read()
    encoded_icerik = base64.b64encode(icerik_bytes).decode("utf-8")

    url = f"https://api.github.com/repos/{kullanici}/{repo}/contents/{dosya_adi}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    sha_degeri = None
    try:
        kontrol_req = requests.get(url, headers=headers, params={"ref": branch}, timeout=10, verify=False)
        if kontrol_req.status_code == 200:
            sha_degeri = kontrol_req.json().get("sha")
            print("    -> Mevcut dosya bulundu, güncelleme yapılıyor...")
        elif kontrol_req.status_code == 404:
            print("    -> Dosya henüz depoda yok, yeni dosya oluşturuluyor...")
    except Exception as e:
        print(f"    [!] GitHub kontrol hatası: {e}")

    anlik_tarih = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    payload = {
        "message": f"Özel Canlı Maç, UFC, TKGS ve Sinema/Dizi IPTV Listesi: {anlik_tarih}",
        "content": encoded_icerik,
        "branch": branch
    }
    if sha_degeri:
        payload["sha"] = sha_degeri

    try:
        yukle_req = requests.put(url, headers=headers, data=json.dumps(payload), timeout=20, verify=False)
        if yukle_req.status_code in (200, 201):
            raw_url = f"https://raw.githubusercontent.com/{kullanici}/{repo}/{branch}/{dosya_adi}"
            print("\n========================================================")
            print(" [BAŞARILI] Özel Spor, UFC, TKGS & Sinema Listesi GitHub'a Yüklendi!")
            print(f" Televizyon Linki:\n -> {raw_url}")
            print("========================================================\n")
            return raw_url
        else:
            print(f"\n[HATA] Yükleme başarısız! Kod: {yukle_req.status_code}")
            print(yukle_req.text)
            return None
    except Exception as e:
        print(f"\n[!] GitHub API hatası: {e}")
        return None


def main():
    print("=" * 60)
    print("  ÖZEL CANLI MAÇ, UFC, ŞAMPİYONLAR LİGİ, TKGS & VOD BOTU")
    print("=" * 60)

    config = load_config()
    github_cfg = config.get("github", {})
    cikti_dosyasi = github_cfg.get("dosya_adi", DEFAULT_OUTPUT_FILE)

    sirali_kanallar = kanallari_tara_sirala_ve_filtrele(config)

    if not sirali_kanallar:
        print("\n[!] Aktif kanal bulunamadı.")
        return

    m3u_dosyasi_kaydet(sirali_kanallar, cikti_dosyasi)
    github_api_ile_yukle(cikti_dosyasi, github_cfg)


if __name__ == "__main__":
    main()
