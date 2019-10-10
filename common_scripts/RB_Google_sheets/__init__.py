import clr
import sys
import os
import math
from RedBimEngine.constants import GOOGLE
from common_scripts import echo

sys.path.append(GOOGLE)
clr.AddReference("Google.Apis")
clr.AddReference("Google.Apis.Auth")
clr.AddReference("Google.Apis.Core")
clr.AddReference("Google.Apis.Sheets.v4")

from Google.Apis.Auth.OAuth2 import *
from Google.Apis.Sheets.v4 import *
from Google.Apis.Sheets.v4.Data import *
from Google.Apis.Services import *
from Google.Apis.Util.Store import *
from System.IO import FileStream, FileMode, FileAccess
from System.Threading import CancellationToken


class RB_Google_sheets:
    def __init__(self):
        self.Scopes = [SheetsService.Scope.Spreadsheets]
        self.ApplicationName = "RedBim"
        self.stream = FileStream(os.path.join(GOOGLE, 'credentials.json'),
                            FileMode.Open, FileAccess.Read)
        self.credPath = os.path.join(GOOGLE, "token.json")
        self.credential = GoogleWebAuthorizationBroker.AuthorizeAsync(
            GoogleClientSecrets.Load(self.stream).Secrets,
            self.Scopes,
            "user",
            CancellationToken.None,
            FileDataStore(self.credPath, True)).Result
        BCS = BaseClientService.Initializer()
        BCS.HttpClientInitializer = self.credential
        BCS.ApplicationName = self.ApplicationName
        self.service = SheetsService(BCS)

    def sec_index(self, x):
        x = x + 1
        alphabet = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        word = ''
        count_of_sec_index = 0
        x_iterator = x
        while x_iterator  > 0:
            count_of_sec_index += 1
            x_iterator = x_iterator // (len(alphabet) + 1)
        for i in range(count_of_sec_index - 1, -1, -1):
            step_count = int(math.pow(len(alphabet), i))
            word_numb = x // step_count
            x = x - step_count * word_numb
            word += alphabet[word_numb - 1]
        return word

    def index_from_set(self, el):
        x = self.sec_index(el[0])
        y = str(el[1] + 1)
        return x + y

    def get_range_from_arrs(self, arr, start=(0, 0)):
        coord_1 = self.index_from_set(start)
        coord_2 = self.index_from_set((len(arr) - 1, len(arr[0]) - 1))
        return coord_1 + ':' + coord_2



    def append_by_range(self, spreadsheetId, values, start = (0, 0)):
        oblist = values
        valueRange = ValueRange()
        valueRange.Values = oblist
        range = self.get_range_from_arrs(values)
        appendRequest = self.service.Spreadsheets.Values.Append(valueRange, spreadsheetId, range)
        appendRequest.ValueInputOption = SpreadsheetsResource.ValuesResource.AppendRequest.ValueInputOptionEnum.USERENTERED
        response = appendRequest.Execute()
        return response
