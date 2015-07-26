module GameSaver where
{-| Elm app for saving foosball games
-}
import Char
import Html exposing (..)
import Html.Attributes as Attr exposing (..)
import Html.Events exposing (..)
import Html.Lazy exposing (lazy, lazy2, lazy3)
import Http
import Json.Decode as Json exposing ((:=))
import Json.Encode
import String
import Task exposing (..)
import Signal exposing (Signal, Address)

---- MODEL ----
type alias Model =
    { players : List Player
    , field : String
    , uid : Int
    , visibility : String
    }


type alias Player =
    { name : String
    , editing : Bool
    , id : Int
    }


newTask : String -> Int -> Player
newTask pname id =
    { name = pname
    , editing = False
    , id = id
    }

emptyModel : Model
emptyModel =
    { players = []
    , visibility = "All"
    , field = ""
    , uid = 0
    }

-- UPDATE
type Action = NoOp |
              Add |
              UpdateField String |
              Delete Int |
              DeleteComplete |
              EditingPlayer Int Bool |
              UpdatePlayer Int String

-- How we update our Model on a given Action?
update : Action -> Model -> Model
update action model =
    case action of
      NoOp -> model

      Add ->
          { model |
              uid <- model.uid + 1,
              field <- "",
              players <-
                  if String.isEmpty model.field
                    then model.players
                    else model.players ++ [newTask model.field model.uid]
          }

      UpdateField str ->
          { model | field <- str }

      EditingPlayer id isEditing ->
          let updateTask t = if t.id == id then { t | editing <- isEditing } else t
          in
              { model | players <- List.map updateTask model.players }

      UpdatePlayer id player ->
          let updateTask t = if t.id == id then { t | name <- player } else t
          in
              { model | players <- List.map updateTask model.players }

      Delete id ->
          { model | players <- List.filter (\t -> t.id /= id) model.players }

-- VIEW
view : Address Action -> Model -> Html
view address model =
    div
      [ class "fbrec-wrapper" ]
      [ section
          [ id "fb_record" ]
          [ lazy2 playerEntry address model.field
          , lazy2 playerList address model.players
          ]
      ]


playerEntry : Address Action -> String -> Html
playerEntry address player =
    header
        [ id "header" ]
        [ h1 [] [ text "Player Entry" ]
        , input
            [ id "new-player"
            , placeholder "Enter player name"
            , autofocus True
            , value player
            , name "newPlayer"
            , on "input" targetValue (Signal.message address << UpdateField)
            , onEnter address Add
            ]
            []
        ]

playerList : Address Action -> List Player -> Html
playerList addr players =
    section
      [ id "main" ]
      [ ul [ id "player-list" ] (List.map (playerItem addr) players) ]

playerItem : Address Action -> Player -> Html
playerItem addr playa =
    li
      [ classList [("editing", playa.editing)] ]
      [ div
          [ class "playerItem" ]
          [ label
              [ onDoubleClick addr (EditingPlayer playa.id True) ]
              [ text playa.name ]
          , button [ class "btn btn-danger",
                     onClick addr (Delete playa.id) ]
          [ span [class "glyphicon glyphicon-remove",
                 property "aria-hidden" (Json.Encode.string "true")]
           []
          ]
          ]
      ]

onEnter : Address a -> a -> Attribute
onEnter address value =
    on "keydown"
      (Json.customDecoder keyCode is13)
      (\_ -> Signal.message address value)


is13 : Int -> Result String ()
is13 code =
  if code == 13 then Ok () else Err "not the right key code"

-- WIRING
---- INPUTS ----

-- wire the entire application together
main : Signal Html
main =
  Signal.map (view actions.address) model


-- manage the model of our application over time
model : Signal Model
model =
  Signal.foldp update initialModel actions.signal


initialModel : Model
initialModel =
  Maybe.withDefault emptyModel getStorage


-- actions from user input
actions : Signal.Mailbox Action
actions =
  Signal.mailbox NoOp

-- interactions with server to save the model
port getStorage : Maybe Model

port setStorage : Signal Model
port setStorage = model