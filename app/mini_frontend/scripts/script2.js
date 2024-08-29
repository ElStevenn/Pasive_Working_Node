
spongebob_images = [
    "https://imgflip.com/s/meme/Mocking-Spongebob.jpg","https://media.tenor.com/D5bFxOZk_S4AAAAe/patrick-star.png",
    "https://i.pinimg.com/736x/27/e0/2e/27e02eadbe6a321a7d0a9641a394c811.jpg","https://i.kym-cdn.com/entries/icons/original/000/009/803/spongebob-squarepants-patrick-spongebob-patrick-star-background-225039.jpg",
    "https://media.tenor.com/Bk2KgJSNu5EAAAAe/patrick-star-crying.png","https://i.pinimg.com/564x/c6/5b/c9/c65bc916f1d6d167a5a027f35557f983.jpg",
    "https://i.kym-cdn.com/entries/icons/facebook/000/026/111/4917038d8bbd7fe362bed691690c7da4.jpg","https://i.pinimg.com/736x/47/f9/85/47f98539ae54d4968a2d5ae5f24cc21c.jpg",
    "https://i.kym-cdn.com/entries/icons/original/000/000/506/Screen_Shot_2021-03-18_at_4.23.26_PM.png","https://content.imageresizer.com/images/memes/Angry-mr-krabs-and-angry-spongebob-meme-8.jpg",
    "https://i.pinimg.com/736x/f5/8b/23/f58b2313083dc2b197da94070885c5a3.jpg","https://i.pinimg.com/originals/b9/15/56/b91556f620d03029f0300fa047c6cfc6.jpg",
    "https://pbs.twimg.com/media/EVf10BbXgAE-iWs.jpg","",
    "","",
    "","",
    "","",
    "","",
];

messages_meme = [
    "",""
]
const now = new Date();

document.addEventListener('DOMContentLoaded', function () {
    console.log("Hey! this is script2!");
    let used = false;

    function create_row_element(date, time, zone, currency, importance, event, actual, previous) {
        const rowElement = document.createElement('tr');
        const bellIcon = `
            <div class="bell-icon-container">
                <span class="tooltip">Create_Alert</span>
                <img src="mini_frontend/images/add.png" alt="Bell Icon" class="bell-icon">
                <div class="create-alert">
                    <h4>Create Alert</h4>
                    <p>MBA Mortgage Applications</p>
                    <label><input type="radio" name="frequency" value="once"> Once</label><br>
                    <label><input type="radio" name="frequency" value="recurring" checked> Recurring</label><br>
                    <label><input type="checkbox" name="reminder"> Send me a reminder</label>
                    <select>
                        <option>15 minutes before</option>
                        <option>30 minutes before</option>
                        <option>1 hour before</option>
                    </select>
                    <p>Delivery Method</p>
                    <label><input type="checkbox" checked> Website popup</label><br>
                    <label><input type="checkbox" checked> Mobile App notifications</label>
                    <a href="#">Manage my alerts »</a>
                    <button class="create-button">Create</button>
                </div>
            </div>
        `;

        let stars = '';

        if (!actual) {
            actual = '';
        }
        if (!previous) {
            previous = '';
        }

        const currentHours = now.getHours();
        const currentMinutes = now.getMinutes();
        const currentTimeString = `${currentHours.toString().padStart(2, '0')}:${currentMinutes.toString().padStart(2, '0')}`; 

        const currentTime = new Date(`1970-01-01T${currentTimeString}:00`);
        const rowTime = new Date(`1970-01-01T${time}:00`);

        if (rowTime > currentTime && used == false) {
            rowElement.style.borderBottom = "3px solid #e6fcff";
            used = true;
        }

        const starImage = '<img src="mini_frontend/images/star.png" alt="Star" style="width: 17px; height: 17px; margin-left: 3px;">';

        if (importance === "low") {
            stars = starImage;
        } else if (importance === "medium") {
            stars = starImage + starImage;
        } else if (importance === "high") {
            stars = starImage + starImage + starImage;
        } else {
            stars = 'Error occurred';
        }

        rowElement.innerHTML = `
            <td>${date}</td>
            <td>${time}</td>
            <td>${zone}</td>
            <td>${currency}</td>
            <td>${stars}</td>
            <td>${event}</td>
            <td>${actual}</td>
            <td class="bell-cell">${previous} ${bellIcon}</td>
        `;
        
        return rowElement;
    }

    function get_all_events() {
        const url = '/economic_calendar/today_events';

        return fetch(url)
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => {
                        console.log(`Show something on the screen according to the error: ${err}`);
                        throw new Error('Fetch error');
                    });
                }
                return response.json();
            })
            .then(data => {
                return data;
            })
            .catch(error => {
                console.log("An error occurred: ", error);
                return {};
            });
    }

    function set_images_right(rows) {
        let result = ''
        if (rows.length === 0) {
            result = `
            <img src="https://i.pinimg.com/736x/ed/19/fd/ed19fd619e3281cdb02dafb39d44f4d1.jpg" alt="Bored funny meme" class="meme">
            <p>There is no events today ✨</p>
            `;
        } else if (rows.length < 5) {
            // Add more logic if needed
        }
    }

    const loadingElement = document.getElementById('loading');
    loadingElement.style.display = 'flex';

    get_all_events().then(rows => {
        const eventList = document.getElementById('calendar-content');
        const imageList = document.getElementById('meme-container-div');

        console.log(rows.length);

        loadingElement.style.display = 'none';

        if (!eventList) {
            console.error("Error: 'calendar-content' element not found in the DOM.");
            return;
        }

        console.log("rows ->", rows);

        if (!rows || rows.length === 0) {
            const no_events_element = document.createElement('tr');
            no_events_element.innerHTML = '<td colspan="100%">There are no events today</td>';
            eventList.appendChild(no_events_element);
        } else {
            rows.forEach(row => {
                const { date, time, zone, currency, importance, event, actual, previous } = row;
                const eventElement = create_row_element(date, time, zone, currency, importance, event, actual, previous);
                eventList.appendChild(eventElement);
            });
        }

        let dogma_right = set_images_right(rows);

    }).catch(error => {
        console.error('Error handling events:', error);
        loadingElement.style.display = 'none';
        const eventList = document.getElementById('calendar-content');
        if (eventList) {
            const errorElement = document.createElement('tr');
            errorElement.innerHTML = '<td colspan="100%">An error occurred while fetching events.</td>';
            eventList.appendChild(errorElement);
        } else {
            console.error("Error: 'calendar-content' element not found in the DOM.");
        }
    });
    

});


document.addEventListener('DOMContentLoaded', function() {
    // Add click event to each bell icon
    document.querySelectorAll('.bell-icon').forEach(bell => {
        bell.addEventListener('click', function(event) {
            event.stopPropagation();
            const alertBox = this.parentElement.querySelector('.create-alert');

            // Close other alert boxes
            document.querySelectorAll('.create-alert').forEach(box => {
                if (box !== alertBox) {
                    box.style.visibility = 'hidden';
                    box.style.opacity = '0';
                }
            });

            // Toggle visibility for clicked bell's alert box
            alertBox.style.visibility = 'visible';
            alertBox.style.opacity = '1';
        });
    });

    // Hide the alert box when clicking outside of it
    document.addEventListener('click', function() {
        document.querySelectorAll('.create-alert').forEach(alertBox => {
            alertBox.style.visibility = 'hidden';
            alertBox.style.opacity = '0';
        });
    });

    // Prevent hiding the alert box when clicking inside it
    document.querySelectorAll('.create-alert').forEach(alertBox => {
        alertBox.addEventListener('click', function(event) {
            event.stopPropagation();
        });

        // Add click event to the "Create" button to hide the alert box
        alertBox.querySelector('.create-button').addEventListener('click', function() {
            alertBox.style.visibility = 'hidden';
            alertBox.style.opacity = '0';
        });
    });
});


// PART II
function generateFunFact() {
    const funFacts = [
        "Did you know? The stock market was once closed for almost 4 months during World War I!",
        "Fun Fact: The NYSE was founded in 1792 under a buttonwood tree.",
        "Did you know? The first stock ever traded was the Dutch East India Company in 1602.",
        "Fun Fact: The longest bear market in history lasted for 929 days.",
        "Did you know? You can buy stocks in a company that makes the 'Smiley Face' emoji!",
        "Fun Fact: Warren Buffett bought his first stock at age 11.",
        "Did you know? The shortest war in history lasted 38 minutes. But the market can drop even faster!",
        "Fun Fact: There's a stock exchange on the moon in a sci-fi novel!"
    ];
    const randomIndex = Math.floor(Math.random() * funFacts.length);
    document.getElementById('fun-fact').textContent = funFacts[randomIndex];
}

function quickMarketTrends() {
    const trends = [
        "Stocks are sizzling hot! Buy low, sell high!",
        "Market is cooler than a cucumber. Stay calm and invest on.",
        "Investors are in panic mode! Time to buy the dip?",
        "Bulls are running wild! Hold on tight to your stocks!",
        "Bear market incoming? Or just a small nap for the bulls?",
    ];
    alert(trends[Math.floor(Math.random() * trends.length)]);
}

function instantReactionGauge() {
    const reactions = [
        "Investors just gasped! What's happening?",
        "Everyone's buying! It's a frenzy!",
        "Panic sell-off! Get out while you can!",
        "Stocks are mooning! To the stars!",
        "Complete silence... Is this the calm before the storm?"
    ];
    alert(reactions[Math.floor(Math.random() * reactions.length)]);
}

function randomStockPicker() {
    const stocks = [
        "Tesla (TSLA) - Time for an electric ride!",
        "Amazon (AMZN) - Shopping spree!",
        "Apple (AAPL) - An apple a day keeps the losses away!",
        "GameStop (GME) - Ready for some memes?",
        "Bitcoin (BTC) - To the moon or the basement?"
    ];
    alert("Your random stock pick is: " + stocks[Math.floor(Math.random() * stocks.length)]);
}