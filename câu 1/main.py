from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time

# URL của trang fbref chứa thống kê Ngoại hạng Anh mùa 2023-2024
url = "https://fbref.com/en/comps/9/2023-2024/stats/2023-2024-Premier-League-Stats"

# Khởi tạo trình duyệt Chrome
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
driver.get(url)
driver.implicitly_wait(10)  # Đợi trang tải

# Thêm thời gian chờ để đảm bảo bảng dữ liệu đã được tải hoàn tất
time.sleep(5)
page_content = driver.page_source
driver.quit()

# Phân tích nội dung trang với BeautifulSoup
soup = BeautifulSoup(page_content, 'html.parser')
table = soup.find('table', {'id': 'stats_standard'})

if table:
    print("Tìm thấy bảng dữ liệu cầu thủ!")

    # Các cột cần thu thập theo yêu cầu
    required_stats = [
        'player', 'nation', 'team', 'position', 'age',
        # Playing time
        'games', 'starts', 'minutes',
        # Performance
        'goals', 'pens_made', 'assists', 'yellow_cards', 'red_cards',
        # Expected
        'xg', 'npxg', 'xa',
        # Progression
        'progressive_carries', 'progressive_passes', 'progressive_receptions',
        # Per 90 minutes
        'goals_per90', 'assists_per90', 'goals_assists_per90', 'non_penalty_goals_per90', 'goals_assists_minus_pens_per90',
        'xg_per90', 'xa_per90', 'xg_xa_per90', 'npxg_per90', 'npxg_xa_per90',
        # Goalkeeping
        'goals_against', 'goals_against_per90', 'shots_on_target_against', 'saves', 'save_pct', 'wins', 'draws',
        'losses', 'clean_sheets', 'clean_sheets_pct', 'pens_att', 'pens_allowed', 'pens_saved', 'pens_missed', 'save_pct',
        # Shooting
        'shots', 'shots_on_target', 'shots_on_target_pct', 'shots_per90', 'shots_on_target_per90', 'goals_per_shot',
        'goals_per_shot_on_target', 'average_shot_distance', 'fk_goals', 'penalty_kicks', 'penalty_kick_attempts',
        # Passing
        'passes_completed', 'passes', 'passes_completed_pct', 'passes_total_distance', 'progressive_pass_distance',
        'short_passes_completed', 'short_passes', 'short_passes_completed_pct',
        'medium_passes_completed', 'medium_passes', 'medium_passes_completed_pct',
        'long_passes_completed', 'long_passes', 'long_passes_completed_pct',
        'assists', 'xa', 'xa_per90', 'key_passes', 'passes_into_final_third', 'passes_into_penalty_area',
        'crosses_into_penalty_area', 'progressive_passes',
        # Defensive Actions
        'tackles', 'tackles_won', 'def_3rd_tackles', 'mid_3rd_tackles', 'att_3rd_tackles', 'challenges',
        'challenge_wins', 'challenge_pct', 'blocks', 'shots_blocked', 'passes_blocked', 'interceptions',
        'tackles_interceptions', 'clearances', 'errors',
        # Possession
        'touches', 'touches_def_pen_area', 'touches_def_3rd', 'touches_mid_3rd', 'touches_att_3rd', 'touches_att_pen_area',
        'touches_live_ball', 'take_ons', 'take_ons_won', 'take_ons_won_pct', 'take_ons_tackled', 'take_ons_tackled_pct',
        'carries', 'carries_total_distance', 'carries_progressive_distance', 'progressive_carries',
        'carries_into_final_third', 'carries_into_penalty_area', 'miscontrols', 'dispossessed', 'passes_received',
        'progressive_passes_received'
    ]

    # Danh sách chứa dữ liệu từng cầu thủ
    players_data = []

    # Duyệt qua từng hàng trong bảng
    for row in table.find_all('tr', {'data-row': True}):
        player_data = {cell.get('data-stat'): cell.text.strip() for cell in row.find_all(['th', 'td'])}

        # Xử lý cột "minutes" để lọc cầu thủ có số phút > 90
        minutes_cell = row.find('td', {'data-stat': 'minutes'})
        try:
            player_data['csk_minutes'] = int(
                minutes_cell.get('csk', '0').replace(',', '')) if minutes_cell and minutes_cell.get('csk') else 0
        except ValueError:
            player_data['csk_minutes'] = 0

        players_data.append(player_data)

    # Chuyển dữ liệu thành DataFrame của pandas
    players_df = pd.DataFrame(players_data)

    # Lọc cầu thủ có số phút thi đấu > 90
    filtered_players_df = players_df[players_df['csk_minutes'] > 90].copy()

    # Chọn các cột cần thiết và thay giá trị thiếu bằng 'N/a'
    available_stats = [stat for stat in required_stats if stat in filtered_players_df.columns]
    filtered_players_df = filtered_players_df[available_stats].fillna('N/a')

    # Sắp xếp theo tên cầu thủ và tuổi giảm dần, rồi xóa cột 'csk_minutes'
    filtered_players_df = filtered_players_df.sort_values(by=['player', 'age'], ascending=[True, False])

    # Xuất dữ liệu ra file CSV
    filtered_players_df.to_csv('results.csv', index=False)
    print("Dữ liệu đã được lưu vào tệp 'results.csv'")
else:
    print("Không tìm thấy bảng dữ liệu.")
